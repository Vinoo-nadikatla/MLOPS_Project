# src/models/two_stage_model.py
"""
Two-Stage ML Pipeline:
1. Stage 1: Random Forest for Prediction - predict likelihood/risk scores
2. Stage 2: Hungarian Algorithm for Optimal Assignment - assign resources based on predictions
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from scipy.optimize import linear_sum_assignment
import joblib
import os

class TwoStageModel:
    """Combines Random Forest predictions with Hungarian Algorithm for optimal assignment"""
    
    def __init__(self, rf_model=None):
        """
        Initialize two-stage model.
        Args:
            rf_model: Trained RandomForestClassifier or None
        """
        self.rf_model = rf_model
        self.feature_names = None
    
    def fit(self, X, y):
        """
        Stage 1: Train Random Forest model
        Args:
            X: Feature matrix (n_samples, n_features)
            y: Target labels
        """
        self.rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.rf_model.fit(X, y)
        self.feature_names = X.columns.tolist() if isinstance(X, pd.DataFrame) else None
        print(f"✓ Random Forest trained with {len(X)} samples")
        return self
    
    def predict_probabilities(self, X):
        """
        Stage 1: Get prediction probabilities from Random Forest
        Args:
            X: Feature matrix (n_samples, n_features)
        Returns:
            Probability matrix (n_samples, n_classes)
        """
        if self.rf_model is None:
            raise ValueError("Model not trained. Call fit() first.")
        return self.rf_model.predict_proba(X)
    
    def predict_labels(self, X):
        """
        Stage 1: Get predicted labels from Random Forest
        Args:
            X: Feature matrix (n_samples, n_features)
        Returns:
            Predicted labels
        """
        if self.rf_model is None:
            raise ValueError("Model not trained. Call fit() first.")
        return self.rf_model.predict(X)
    
    def hungarian_assignment(self, cost_matrix, maximize=False):
        """
        Stage 2: Hungarian Algorithm for optimal assignment
        Solves the assignment problem - matches workers to tasks optimally.
        
        Args:
            cost_matrix: Square matrix of costs (n x n)
                        - Rows represent workers/resources
                        - Cols represent tasks/slots
            maximize: If True, maximize assignments; if False, minimize
        
        Returns:
            Dictionary with assignment details:
            - 'worker_task_pairs': list of (worker_idx, task_idx) assignments
            - 'total_cost': sum of assignment costs
            - 'cost_matrix': original cost matrix used
        """
        cost_matrix = np.array(cost_matrix, dtype=float)
        
        # Convert maximization to minimization (negate costs)
        if maximize:
            cost_matrix = -cost_matrix
        
        # Run Hungarian Algorithm (linear sum assignment)
        worker_indices, task_indices = linear_sum_assignment(cost_matrix)
        
        # Calculate total cost
        total_cost = cost_matrix[worker_indices, task_indices].sum()
        
        # Convert back if it was maximization
        if maximize:
            total_cost = -total_cost
        
        return {
            'worker_task_pairs': list(zip(worker_indices.tolist(), task_indices.tolist())),
            'total_cost': float(total_cost),
            'cost_matrix': cost_matrix.tolist()
        }
    
    def predict_and_assign(self, X, n_tasks=None, maximize=False):
        """
        Combined two-stage prediction and assignment
        
        Args:
            X: Feature matrix (n_samples, n_features)
            n_tasks: Number of tasks/slots. If None, uses n_samples
            maximize: If True, maximize scores; if False, minimize
        
        Returns:
            Dictionary with predictions and assignments
        """
        # Stage 1: Get probabilities from Random Forest
        probs = self.predict_probabilities(X)
        labels = self.predict_labels(X)
        
        # Use positive class probability as likelihood score
        scores = probs[:, 1] if probs.shape[1] > 1 else probs[:, 0]
        
        # Stage 2: Create cost matrix and run Hungarian Algorithm
        n_workers = len(X)
        n_tasks = n_tasks or n_workers
        
        # Create cost matrix based on predicted probabilities
        # Replicate scores to fill cost matrix (n_workers x n_tasks)
        if n_workers == n_tasks:
            # Square matrix: use scores as costs
            cost_matrix = np.diag(scores)
            # Fill off-diagonal with average scores for complete assignment
            for i in range(n_workers):
                for j in range(n_tasks):
                    if i != j:
                        cost_matrix[i, j] = scores[i] * 0.5  # penalize non-diagonal
        else:
            # Non-square: expand or contract to n_tasks
            cost_matrix = np.zeros((n_workers, n_tasks))
            for i in range(n_workers):
                for j in range(n_tasks):
                    # Assign based on scores and task index
                    cost_matrix[i, j] = scores[i] * (1 - (j % len(scores)) / len(scores))
        
        assignment_result = self.hungarian_assignment(cost_matrix, maximize=maximize)
        
        return {
            'predictions': labels.tolist(),
            'probabilities': scores.tolist(),
            'n_samples': n_workers,
            'n_tasks': n_tasks,
            'assignment': assignment_result,
            'optimal_assignments': assignment_result['worker_task_pairs'],
            'total_assignment_score': assignment_result['total_cost']
        }
    
    def save(self, model_path):
        """Save two-stage model"""
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        joblib.dump({
            'rf_model': self.rf_model,
            'feature_names': self.feature_names
        }, model_path)
        print(f"✓ Two-stage model saved to {model_path}")
    
    def load(self, model_path):
        """Load two-stage model"""
        data = joblib.load(model_path)
        self.rf_model = data['rf_model']
        self.feature_names = data['feature_names']
        print(f"✓ Two-stage model loaded from {model_path}")
        return self
