import pandas as pd
import json
import os
from sklearn.metrics import precision_score, recall_score, f1_score, confusion_matrix

def main():
    """
    Evaluate the performance of detection heuristics against ground truth.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(os.path.dirname(os.path.dirname(script_dir)), "data")
    output_dir = os.path.join(data_dir, "prof_writing_analytics")
    
    print("Loading data for evaluation...")
    preds = pd.read_csv(os.path.join(output_dir, "predictions.csv"))
    staff = pd.read_csv(os.path.join(data_dir, "Newspaper_Staff.csv"))
    
    # Evaluate at the USER level to avoid skewing metrics based on post volume
    user_preds = preds.groupby('user_id').agg({
        'is_professional_temporal': 'max',
        'is_professional_topic': 'max',
        'is_professional_content': 'max',
        'is_professional_impact': 'max'
    }).reset_index()
    
    # Create ground truth label: 1 if in staff, 0 otherwise
    staff_ids = set(staff['ID_User'].tolist())
    user_preds['y_true'] = user_preds['user_id'].apply(lambda x: 1 if x in staff_ids else 0)
    
    # Ensemble prediction (if ANY of the 4 methods flagged the user)
    user_preds['y_pred_any'] = (
        user_preds['is_professional_temporal'] |
        user_preds['is_professional_topic'] |
        user_preds['is_professional_content'] |
        user_preds['is_professional_impact']
    ).astype(int)
    
    metrics = {}
    
    eval_columns = [
        'is_professional_temporal',
        'is_professional_topic',
        'is_professional_content',
        'is_professional_impact',
        'y_pred_any'
    ]
    
    for col in eval_columns:
        y_true = user_preds['y_true']
        y_pred = user_preds[col]
        
        p = precision_score(y_true, y_pred, zero_division=0)
        r = recall_score(y_true, y_pred, zero_division=0)
        f1 = f1_score(y_true, y_pred, zero_division=0)
        cm = confusion_matrix(y_true, y_pred, labels=[0, 1]).tolist()
        
        metrics[col] = {
            'precision': round(p, 4),
            'recall': round(r, 4),
            'f1_score': round(f1, 4),
            'confusion_matrix': {
                'True_Negatives': cm[0][0],
                'False_Positives': cm[0][1],
                'False_Negatives': cm[1][0],
                'True_Positives': cm[1][1]
            }
        }
    
    # Overall statistics
    metrics['overall_stats'] = {
        'total_users_analyzed': int(len(user_preds)),
        'total_staff_in_data': int(sum(user_preds['y_true'])),
        'total_flagged_by_any_method': int(sum(user_preds['y_pred_any']))
    }
    
    output_file = os.path.join(output_dir, "model_quality_metrics.json")
    with open(output_file, 'w') as f:
        json.dump(metrics, f, indent=4)
        
    print(f"Metrics evaluated and saved to {output_file}")
    
    print("\n--- Summary of Model Metrics ---")
    for col in eval_columns:
        print(f"{col}: Precision={metrics[col]['precision']}, Recall={metrics[col]['recall']}")

if __name__ == "__main__":
    main()
