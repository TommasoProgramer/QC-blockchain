import hashlib
import socket
import pickle
import random
import subprocess
import time
from XMSS import XMSS
import qiskit 
import time
from smart_contract import SmartContract

# Define the Wallet class
class Wallet:
    def __init__(self):
        self.private_key = XMSS()  # Generate private key for the wallet
        self.public_key = self.private_key.get_public_key()  # Get corresponding public key
        self.balance = 0

    def get_wallet_address(self):
        # The wallet address is derived from the XMSS public key using a cryptographic hash function
        return hashlib.sha256(self.public_key.encode()).hexdigest()

    def add_tokens(self, amount):
        # Add tokens to the wallet balance
        self.balance += amount

    def transfer_tokens(self, recipient_address, amount):
        # Transfer tokens to the recipient wallet
        if self.balance >= amount:
            self.balance -= amount
            if recipient_address in wallet_addresses:
                wallet_addresses[recipient_address].balance += amount
                print(f"Transaction successful. {amount} qc tokens transferred to {recipient_address}")
            else:
                print("Error: Recipient address not found.")
        else:
            print("Error: Insufficient balance for the transaction.")

    # Initialize wallet addresses dictionary
wallet_addresses = {}

def xmss_signature(private_key, message):
    """
    Generate a quantum-resistant XMSS signature for the given message using the private key.
    """
    return hashlib.sha256(f"{private_key}{message}".encode()).hexdigest()

def xmss_verify_signature(public_key, message, signature):
    """
    Verify the quantum-resistant XMSS signature for the given message using the public key.
    """
    return signature == xmss_signature(public_key, message)
   


class QcashBlockchain:
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.create_genesis_block()
        self.user_public_keys = {}
        self.nodes = set()  # Set to store addresses of participating nodes
        self.host = "localhost"  # For simplicity, use localhost as the host
        self.port = 49467  # Port for node communication
        self.private_key = XMSS()  # Generate private key for the node
        self.public_key = self.private_key.get_public_key()  # Get corresponding public key
        self.price_per_qc = 0.01  # Set the starting price in cents (change this value as needed)
        self.smart_contract = SmartContract()

    def generate_wallet_address(self):
        # Generate a new private key for the wallet using XMSS
        private_key = XMSS()
        # Get the corresponding public key (wallet address)
        wallet_address = private_key.get_public_key()
        return wallet_address, private_key

    def create_genesis_block(self):
        # Create the first block (genesis block) with arbitrary values
        genesis_block = {
            'index': 1,
            'transactions': [],
            'proof': 100,  # Placeholder proof for simplicity
            'previous_hash': '1',  # Placeholder for the first block
            'timestamp': time.time()
        }
        # Calculate the hash of the genesis block
        genesis_block['hash'] = self.calculate_hash(genesis_block)
        # Append the genesis block to the chain
        self.chain.append(genesis_block)

    def mine_block(self):
        """
        Mine a new block and add it to the blockchain
        """
        last_block = self.chain[-1]
        proof = self.proof_of_work(last_block['proof'])
        previous_hash = self.calculate_hash(last_block)
        block = {
            'index': len(self.chain) + 1,
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash,
            'timestamp': time.time()
        }
        # Reset the current list of transactions
        self.current_transactions = []
        # Calculate the hash of the block
        block['hash'] = self.calculate_hash(block)
        # Append the block to the chain
        self.chain.append(block)
        return block

   
    def calculate_hash(self, block):
        """
        Calculate the SHA-256 hash of a block
        """
        block_string = str(block).encode()
        return hashlib.sha256(block_string).hexdigest()
    
    def register_node(self, node_address):
        """
        Add a new node to the network
        """
        self.nodes.add(node_address)

    def proof_of_work(self, last_proof):
        """
        Simple proof of work algorithm:
        - Find a number p' such that hash(p * p') contains 4 leading zeroes, where p is the previous proof
        - p is the previous proof, and p' is the new proof
        """
        difficulty_level = 4

        # Use subprocess to run the quantum security script and get the proof-of-work nonce
        result = subprocess.run(["python", "quantum_security.py", str(difficulty_level)], capture_output=True, text=True)
        quantum_proof = int(result.stdout.strip())

        proof = 0
        while self.is_valid_proof(last_proof, proof, quantum_proof) is False:
            proof += 1
        return proof


    def is_valid_proof(self, last_proof, proof, quantum_proof):
        """
        Validate the proof: Does hash(last_proof * proof) contain 4 leading zeroes?
        """
        guess = f"{last_proof}{proof}{quantum_proof}".encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"
    
    def is_valid_block(self, block):
        """
        Check if a received block is valid
        """
        previous_block = self.chain[-1]
        return (
             block['index'] == previous_block['index'] + 1
            and block['previous_hash'] == self.calculate_hash(previous_block)
            and self.is_valid_proof(previous_block['proof'], block['proof'])
        )
    
    def broadcast_transaction(self, transaction):
        """
        Broadcast a new transaction to all nodes in the network
        """
        for node in self.nodes:
            self.send_transaction(node, transaction)

    def send_transaction(self, node_address, transaction):
        """
        Send a transaction to a specific node
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((node_address, self.port))
                s.sendall(pickle.dumps(transaction))
        except ConnectionRefusedError:
            print(f"Connection to node {node_address} refused.")
        except Exception as e:
            print(f"Error occurred while sending transaction to node {node_address}: {e}")

    def discover_nodes(self, node_addresses):
        """
        Discover other nodes and add them to the network
        """
        for address in node_addresses:
            if address != f"{self.host}:{self.port}":
                self.nodes.add(address)

    def authenticate_node(self, node_address):
        """
        Authenticate a node using a quantum-resistant signature scheme
        """
        message = f"{self.host}:{self.port}"
        signature = xmss_signature(self.private_key, message)
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((node_address, self.port))
                s.sendall(pickle.dumps((self.public_key, message, signature)))
                response = s.recv(4096)
                if response == b"authenticated":
                    print(f"Authenticated with node {node_address}")
                    self.nodes.add(node_address)
                else:
                    print(f"Failed to authenticate with node {node_address}")
        except ConnectionRefusedError:
            print(f"Connection to node {node_address} refused.")
        except Exception as e:
            print(f"Error occurred while authenticating with node {node_address}: {e}")

    def start_node(self):
        """
        Start a node and listen for incoming blocks and authentication requests
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            s.listen()
            print("Node listening for incoming blocks and authentication requests...")
            while True:
                conn, addr = s.accept()
                with conn:
                    data = conn.recv(4096)
                    if not data:
                        break
                    if isinstance(pickle.loads(data), tuple):
                        # Received authentication request
                        public_key, message, signature, xmss_verify_signature = pickle.loads(data)
                        if xmss_verify_signature(public_key, message, signature):
                            conn.sendall(b"authenticated")
                        else:
                            conn.sendall(b"failed")
                    else:
                        # Received block
                        block = pickle.loads(data)
                        if self.is_valid_block(block):
                            print(f"Received valid block from node {addr}: {block}")
                            self.chain.append(block)
                        else:
                            print(f"Received invalid block from node {addr}: {block}")

    def synchronize(self):
        """
        Periodically request updates from peers to synchronize the blockchain
        """
        while True:
            time.sleep(10)  # Adjust the time interval for synchronization
            for node in self.nodes:
                self.request_update(node)

    def request_update(self, node_address):
        """
        Request blockchain update from a specific node
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((node_address, self.port))
                s.sendall(b"get_blockchain")
                data = b""
                while True:
                    chunk = s.recv(4096)
                    if not chunk:
                        break
                    data += chunk
                if data:
                    blockchain = pickle.loads(data)
                    if self.is_valid_chain(blockchain):
                        self.chain = blockchain
                        print(f"Synchronized with node {node_address}")
                    else:
                        print(f"Invalid blockchain received from node {node_address}")
        except ConnectionRefusedError:
            print(f"Connection to node {node_address} refused.")
        except Exception as e:
            print(f"Error occurred while requesting update from node {node_address}: {e}")
    
    def add_new_transaction(self, sender, recipient, amount, private_key):
        """
        Add a new transaction to the list of current transactions
        """
        transaction = {
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
            'price_per_qc': self.price_per_qc,  # Include the price_per_qc in the transaction
            'timestamp': time.time()
        }

        # Generate a signature for the transaction using the sender's private key
        transaction_signature = xmss_signature(private_key, transaction)

        # Add the signature to the transaction
        transaction['signature'] = transaction_signature

        self.current_transactions.append(transaction)
        # Mint new QC tokens for the recipient
        self.smart_contract.mint_tokens(recipient, amount)
    
    def process_transactions(self, block):
        """
        Process the transactions in a block and update the balances
        """
        for transaction in block['transactions']:
            sender = transaction['sender']
            recipient = transaction['recipient']
            amount = transaction['amount']
            price_per_qc = transaction['price_per_qc']

            # Calculate the total value of the transaction in cents
            total_value = amount * price_per_qc

            # Update the balances in the user_public_keys dictionary
            self.user_public_keys[sender] -= total_value
            self.user_public_keys[recipient] += total_value
            
# Helper function to create a new node on the local machine
def create_new_node(port):
    node = QcashBlockchain()
    node.port = port
    return node

if __name__ == "__main__":
    # Create the first node
    node1 = create_new_node(49467)

    # Register node1 with itself (for demonstration purposes)
    node1.register_node("127.0.0.1:49467")

    # Create a wallet for Alice
    alice_wallet = Wallet()
    wallet_addresses[alice_wallet.get_wallet_address()] = alice_wallet

    # Create a wallet for Bob
    bob_wallet = Wallet()
    wallet_addresses[bob_wallet.get_wallet_address()] = bob_wallet

    # Transfer tokens from node1's wallet to Alice's wallet
    node1_wallet = Wallet()
    wallet_addresses[node1_wallet.get_wallet_address()] = node1_wallet
    node1_wallet.add_tokens(1000)
    node1_wallet.transfer_tokens(alice_wallet.get_wallet_address(), 200)

    # Transfer tokens from Alice's wallet to Bob's wallet
    alice_wallet.transfer_tokens(bob_wallet.get_wallet_address(), 100)

    # Print wallet balances
    print(f"Alice's wallet address: {alice_wallet.get_wallet_address()}, Balance={alice_wallet.balance} qc")
    print(f"Bob's wallet address: {bob_wallet.get_wallet_address()}, Balance={bob_wallet.balance} qc")
    print(f"Node1's wallet address: {node1_wallet.get_wallet_address()}, Balance={node1_wallet.balance} qc")

    while True:
        print("Menu:")
        print ("1. Generate new wallet address")
        choice = input("Enter your choice: ")
        if choice == "1":
            # Generate a new wallet address
            wallet_address, private_key = node1.generate_wallet_address()
            print("New wallet address:", wallet_address)
            print("Private key:", private_key)