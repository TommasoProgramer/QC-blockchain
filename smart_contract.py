class SmartContract:
    def __init__(self):
        self.wallets = {}
        self.starting_price = 0.01
        self.tokens_in_circulation = 10000000000  # Total supply of QC coins

    def mint_tokens(self, wallet_address, amount):
        if amount > 0:
            if wallet_address not in self.wallets:
                self.wallets[wallet_address] = 0
            self.tokens_in_circulation += amount
            self.wallets[wallet_address] += amount

    def transfer_tokens(self, sender_address, recipient_address, amount):
        if sender_address in self.wallets and self.wallets[sender_address] >= amount:
            self.wallets[sender_address] -= amount
            if recipient_address not in self.wallets:
                self.wallets[recipient_address] = 0
            self.wallets[recipient_address] += amount

    def get_wallet_balance(self, wallet_address):
        return self.wallets.get(wallet_address, 0)

    def get_total_tokens_in_circulation(self):
        return self.tokens_in_circulation

    def get_token_price(self):
        return self.starting_price + self.tokens_in_circulation * 0.0001  # Adjust the price as per your requirement
