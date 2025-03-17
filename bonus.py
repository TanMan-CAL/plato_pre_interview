def generate_script(demonstrations: list[Demonstrations]) -> str:
    """
    :args:
    demonstrations: a list of demonstration data, defined above
    
    :desc:
    consumes the demonstration data and uses LLM calls to convert it into a
    python playwright script. challenges: how to make sure its robust
    and reliable? 
    
    splits the demonstration data as follows:
    - overall trajectory (high-level goal like "ordering food from Chipotle")
    - subtasks (logical groups of actions like "entering an address")
    - individual actions (clicks, typing, scrolling)
    - state transitions (how the UI changed after each action)
    
    :returns:
    a python script
    """
    script = generate_script_header()

    
    for demo in demonstrations:
        # get trajectory details
        trajectory = demo.get("trajectory_decomposition", {})
        trajectory_description = trajectory.get("trajectory_description", "")
        subtasks = trajectory.get("subtasks", [])
        transitions = demo.get("transition_descriptions", [])
        
        # add description as comment in the script
        script += f"\n# {trajectory_description}\n"
        
        # for each subtask
        for subtask_index, subtask in enumerate(subtasks):
            action_description = subtask.get("action_description", {})
            description = action_description.get("description", "")
            action_ids = action_description.get("action_ids", [])
            action_descriptions = action_description.get("action_descriptions", [])
            
            # add subtask description as comment
            script += f"\n# Subtask: {description}\n"
            
            # each action in the subtask
            for i, action_id in enumerate(action_ids):
                action_desc = action_descriptions[i]
                
                # transition information if available
                transition_info = transitions[action_id]
                
                # llm call to generate selector strategies based on transition info
                selectors = generate_selectors(action_desc, transition_info)
                
                # LLM call to determine the Playwright code based on the selectors for best choice
                playwright_action = determine_playwright_action(action_desc, selectors)
                
                # for errors and verifying code
                wait_and_verify = generate_wait_verification(action_desc, transition_info)
                
                # additional comments for each action
                script += f"# {action_desc}\n"
                script += playwright_action + "\n"
                script += wait_and_verify + "\n"
            
                # for error checking and generating the for code given the selector chosen
                next_state = determine_expected_state(subtask.get("transition_description", ""))
                script += generate_code_for_state(next_state) + "\n"
    

    return script

def generate_script_header() -> str:
    return """from playwright.sync_api import sync_playwright, expect
import time

def run(playwright):
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    
    try:
        # Script actions will be inserted here
        pass
    finally:
        context.close()
        browser.close()

with sync_playwright() as playwright:
    run(playwright)
"""

def generate_selectors(action_description: str, transition_info: dict) -> list:
    """
    Use LLM to generate CSS and text-based selector strategies for the given action_description
    
    :args:
    action_description: A string describing the user action
    transition_info: Dictionary containing the before and after state info
    
    :returns:
    A list of selectors with different strategies (text, CSS)
    """

    # this would be an LLM call to generate multiple selectors
    # PROMPT would include the action description and before and after parts of the transition info: 
        # action_description
        # transition_info.get('before_state_description', {}
        # transition_info.get('after_state_description', {}

    # llm call would yield the dict as follows: selector_type -> [{"strategy": "strategy_name", "selector": "selector_value", ...]
    selector_strategies = llm_call(PROMPT)
    return selector_strategies

def determine_playwright_action(action_description: str, selectors: list) -> str:
    """
    use llm call to determine the Playwright action based on the action description based off the best selector
    
    :args:
    action_description: A string describing the user action
    selectors: A list of possible selectors for the element
    
    :returns:
    a string containing the Playwright code for the action
    """

    # this would be an LLM call to determine the best Playwright action
    # PROMPT would include the action_description and the selectors
    
    playwright_code = llm_call(PROMPT)
    return playwright_code

def generate_wait_verification(action_description: str, transition_info: dict) -> str:
    """
    Generate code to wait for and verify the expected state change after an action
    
    :args:
    action_description: A string describing the user action
    transition_info: Dict containing before and after state information
    
    :returns:
     A string containing Playwright code for waiting and verification
    """
    
      # this would be an LLM call to generate verification code
      # PROMPT would include the before and after states of the transisiton and the transition description to handle a case where verification might evenfail
      # and would also verify the the action had the desired effect:
      # transition_info.get('before_state_description', {})}
        #    after state: {transition_info.get('after_state_description', {})}
        #    before state: {transition_info.get('before_state_description', {})}
        #    transition description: {transition_info.get('transition_description', '')}

    wait_verify_code = llm_call(PROMPT)
    return wait_verify_code

def determine_expected_state(transition_description: str) -> dict:
    """
    use llm to determine the expected state after a subtask based on the transition description
    
    :args:
    transition_description: A string describing the state transition
    
    :returns:
    A dictionary describing the expected state
    """

    # this would be an LLM call to determine the expected state as a dict
    # PROMPT would be based on the transition description to determine the expected state with a dictionary that specifies UI changes, expected text tags, expected image tags, etc.
    expected_state = llm_call(PROMPT)
    return expected_state

def generate_code_for_state(expected_state: dict) -> str:
    """
    Generate code to verify that the page is in the expected state
    
    :args:
    expected_state: A dictionary describing the expected state
    
    :returns:
    A string containing Playwright code for state verification
    """
    # this would be an LLM call to generate code for the given state
    # PROMPT would be to generate verification code for the expected_code dict from function determine_expected_state
        # prompt would include to check for UI elements (texts, images, etc.)
        # for error checking ex.(try and except blocks)

    verification_code = llm_call(PROMPT)
    return verification_code

def llm_call(prompt: str):
    """
    Make a call to an LLM API with the given prompt  
    :args:
    
    prompt: The prompt to send to the LLM
    
    :returns:
    The response from the LLM
    """
    # call an API like OpenAI's GPT-4

    return # LLM output
