"""
Script to refactor AmazonApis from user_id parameters to session-based authentication
"""
import re

def refactor_amazon_apis():
    with open('AmazonApis.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Already done: Add helper methods (these were added)
    # Now we need to fix the remaining methods
    
    # Fix show_account
    content = re.sub(
        r'def show_account\(self\) -> Dict\[str, Union\[bool, str, Dict\]\]:\s*"""[^"]*"""[^}]+user_data = self\._get_user_data\(user_id\)',
        '''def show_account(self) -> Dict[str, Union[bool, str, Dict]]:
        """
        Retrieves account-specific information including balance, payment cards, and addresses for the currently logged-in user.
        Returns:
            Dict: A dictionary containing account status, message, and account details including
                  balance, payment cards, and addresses if the user is logged in.
        """
        login_check = self._require_login()
        if login_check:
            return {"account_status": False, "message": login_check["message"]}
        
        user_data = self._get_current_user_data()''',
        content,
        flags=re.DOTALL
    )
    
    # Fix delete_account
    content = re.sub(
        r'def delete_account\(self, user_id: str\) -> Dict\[str, Union\[bool, str\]\]:',
        'def delete_account(self) -> Dict[str, Union[bool, str]]:',
        content
    )
    content = re.sub(
        r'(\s+)"""[^"]*Permanently removes a user account[^"]*"""',
        r'\1"""Permanently removes the currently logged-in user\'s account from the system.\n\1Returns:\n\1    Dict: A dictionary containing deletion status and message. Also clears the current user session.\n\1"""',
        content
    )
    content = re.sub(
        r'if user_id in self\.state\["users"\]:\s+del self\.state\["users"\]\[user_id\]\s+if self\.state\["current_user"\] == user_id:\s+self\.state\["current_user"\] = None\s+return \{"delete_status": True, "message": f"Account for user ID \{user_id\} deleted successfully\."\}',
        '''login_check = self._require_login()
        if login_check:
            return {"delete_status": False, "message": login_check["message"]}
        
        user_id = self._get_current_user_id()
        if user_id in self.state["users"]:
            del self.state["users"][user_id]
            self.state["current_user"] = None
            return {"delete_status": True, "message": "Account deleted successfully."}''',
        content
    )
    
    # Fix remove_payment_card
    content = re.sub(
        r'def remove_payment_card\(self, card_id: str\) -> Dict\[str, Union\[bool, str\]\]:[^}]+user_data = self\._get_user_data\(user_id\)',
        '''def remove_payment_card(self, card_id: str) -> Dict[str, Union[bool, str]]:
        """
        Removes a payment card from the currently logged-in user's account.
        Args:
            card_id (str): The unique identifier of the payment card to remove.
        Returns:
            Dict: A dictionary containing removal status and message indicating whether
                  the card was successfully removed or not found.
        """
        login_check = self._require_login()
        if login_check:
            return {"remove_card_status": False, "message": login_check["message"]}
        
        user_id = self._get_current_user_id()
        user_data = self._get_current_user_data()''',
        content,
        flags=re.DOTALL
    )
    
    # Fix show_payment_cards
    content = re.sub(
        r'def show_payment_cards\(\s*self, user_id: str, page_index: int = 1, page_limit: int = 10\s*\) -> Dict\[str, Union\[bool, List\[Dict\]\]\]:',
        'def show_payment_cards(self, page_index: int = 1, page_limit: int = 10) -> Dict[str, Union[bool, str, List[Dict]]]:',
        content
    )
    
    # Update all remaining methods that take user_id
    methods_to_update = [
        'add_address', 'remove_address', 'show_addresses',
        'add_to_cart', 'remove_from_cart', 'update_cart_item_quantity', 'show_cart',
        'apply_promo_code_to_cart', 'remove_promo_code_from_cart', 'checkout',
        'show_orders', 'add_to_wish_list', 'remove_from_wish_list', 'show_wish_list',
        'submit_product_review', 'ask_product_question', 'answer_product_question',
        'subscribe_prime', 'show_prime_subscriptions', 'request_return', 'show_returns'
    ]
    
    for method in methods_to_update:
        # Remove user_id from signature
        content = re.sub(
            rf'def {method}\(\s*self,\s*user_id:\s*str,\s*',
            f'def {method}(self, ',
            content
        )
        # Add login check at start of method
        pattern = rf'(def {method}\([^)]+\)[^:]+:[^"]+"[^"]+""")'
        replacement = r'\1\n        login_check = self._require_login()\n        if login_check:\n            # Return appropriate error based on method\n            pass\n        \n        user_id = self._get_current_user_id()'
        # This is getting complex, let me write the full file instead
    
    with open('AmazonApis_refactored.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Refactoring attempted - check AmazonApis_refactored.py")

if __name__ == "__main__":
    refactor_amazon_apis()
