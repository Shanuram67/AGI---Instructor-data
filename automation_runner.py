"""
automation_runner.py
A minimal runner that can execute tiny, safe automations using pyautogui.
This is intentionally tiny — automations must be brief and strictly controlled.
"""
import pyautogui
import time

def run_automation(steps: list):
    """
    Executes a list of simple automation steps using pyautogui.

    Args:
        steps: A list of dictionaries, where each dict defines an action.
               Example: [{'action': 'move', 'x': 100, 'y': 200},
                         {'action': 'click'},
                         {'action': 'write', 'text': 'Hello World'}]
    """
    print("Starting automation...")
    
    for step in steps:
        action = step.get('action')
        delay = step.get('delay', 0.5)
        
        # Pause before each step for safety and visibility
        time.sleep(delay) 

        try:
            if action == 'move':
                # Move mouse to specified coordinates
                pyautogui.moveTo(step['x'], step['y'], duration=0.25)
                print(f" -> Moved to ({step['x']}, {step['y']})")
                
            elif action == 'click':
                # Perform a left mouse click
                pyautogui.click()
                print(" -> Clicked")
                
            elif action == 'write':
                # Type the specified text
                pyautogui.write(step['text'], interval=0.1)
                print(f" -> Wrote: '{step['text'][:20]}...'")
                
            elif action == 'press':
                # Press a single key (e.g., 'enter', 'esc', 'ctrl')
                pyautogui.press(step['key'])
                print(f" -> Pressed key: {step['key']}")
            
            else:
                print(f" -> Warning: Unknown action '{action}'. Skipping.")

        except KeyError as e:
            print(f"Error: Missing required argument for action '{action}': {e}")
        except Exception as e:
            print(f"An unexpected error occurred during automation: {e}")

    print("Automation finished.")

if __name__ == "__main__":
    # Example safe automation sequence
    automation_sequence = [
        # Move mouse to the center of the screen
        {'action': 'move', 'x': 500, 'y': 500, 'delay': 1.0},
        # Write some text (e.g., if a text field is selected)
        {'action': 'write', 'text': 'This is a test run.', 'delay': 1.5},
        # Press the Enter key
        {'action': 'press', 'key': 'enter', 'delay': 1.0},
    ]
    
    # NOTE: Run this in a safe environment. PyAutoGUI can take control of your mouse/keyboard.
    # To stop a runaway script, quickly move your mouse to any corner of the screen (Failsafe).
    run_automation(automation_sequence)