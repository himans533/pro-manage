import re

def verify_finally_blocks():
    file_path = r'c:\Users\DELL\Downloads\AdminLoginPanel\AdminLoginPanel\AdminLoginPanel\app.py'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    functions_to_check = [
        'def create_employee_task',
        'def calculate_project_progress',
        'def log_activity',
        'def submit_daily_report',
        'def complete_employee_task'
    ]

    print("Verifying try...finally blocks in critical functions:")
    print("-" * 50)
    
    all_passed = True

    for func_name in functions_to_check:
        # Simple check: find the function definition and look for 'finally:' within its scope (simplified)
        # We'll just check if the text 'finally:' appears after the function definition and before the next unrelated function
        
        # This is a heuristic check, not a full AST parse, but sufficient for this context
        start_index = content.find(func_name)
        if start_index == -1:
            print(f"[FAIL] Function {func_name} not found!")
            all_passed = False
            continue

        # Find the next function definition to limit search scope
        next_def_match = re.search(r'\n@app\.route|\ndef ', content[start_index + len(func_name):])
        
        if next_def_match:
            end_index = start_index + len(func_name) + next_def_match.start()
            func_body = content[start_index:end_index]
        else:
            func_body = content[start_index:] # End of file

        if 'finally:' in func_body and 'conn.close()' in func_body:
            print(f"[PASS] {func_name} contains 'finally' block and closes connection.")
        else:
            print(f"[FAIL] {func_name} is MISSING 'finally' block or conn.close()!")
            print(f"Snippet:\n{func_body[-200:]}")
            all_passed = False

    if all_passed:
        print("\nAll critical functions have proper resource cleanup.")
    else:
        print("\nSome functions are missing cleanup logic.")

if __name__ == "__main__":
    verify_finally_blocks()
