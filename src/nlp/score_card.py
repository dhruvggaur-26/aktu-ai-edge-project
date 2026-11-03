import json
import os

# 'indic_ner_final' ki jagah 'indic_ner_checkpoint' path me daalein
log_path = os.path.abspath("models/pytorch/indic_ner_checkpoint/trainer_state.json")

if os.path.exists(log_path):
    with open(log_path, 'r') as f:
        data = json.load(f)
        
    print("\n--- 🏆 FINAL MODEL SCORE CARD ---")
    
    # Reverse search to find the final evaluation metrics
    for log in reversed(data.get('log_history', [])):
        if 'eval_f1' in log:
            print(f"F1 Score:  {log['eval_f1'] * 100:.2f}%")
            print(f"Precision: {log['eval_precision'] * 100:.2f}%")
            print(f"Recall:    {log['eval_recall'] * 100:.2f}%")
            print(f"Accuracy:  {log['eval_accuracy'] * 100:.2f}%\n")
            break
    else:
        print("Scores JSON mein nahi mile. Check karein ki training ke time eval run hua tha ya nahi.")
else:
    print(f"❌ File nahi mili: {log_path}")