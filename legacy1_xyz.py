from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from decimal import Decimal, InvalidOperation

def separator():
    """Print a line separator for better console readability."""
    print("-" * 60)

def input_amount(max_amount: Decimal, address_C: str) -> Decimal:
    """
    Prompt the user for an amount to send from B to C.
    Ensures the entered amount is > 0 and ≤ max_amount.
    """
    while True:
        try:
            amount = Decimal(input(f"\nEnter the amount to send from B to C (max {max_amount} BTC): "))
            if amount <= Decimal('0'):
                print("Error: Amount must be greater than 0.")
            elif amount > max_amount:
                print(f"Error: Amount cannot exceed {max_amount} BTC.")
            else:
                return amount
        except InvalidOperation:
            print("Error: Invalid amount. Please enter a numeric value.")

def main():
    user = "xyz"
    password = "xyz"
    base_url = f"http://{user}:{password}@127.0.0.1:18443"
    connection = AuthServiceProxy(base_url)
    wallet = "Team_xyz"

    separator()
    print("Initializing Legacy Wallet...")

    try:
        loaded_wallets = connection.listwallets()
        if wallet not in loaded_wallets:
            connection.loadwallet(wallet)
            print(f"Loaded wallet: {wallet}")
        else:
            print(f"Wallet '{wallet}' is already loaded.")
    except JSONRPCException as e:
        print(f"Error loading wallet: {e}")

    connection = AuthServiceProxy(f"{base_url}/wallet/{wallet}")

    separator()
    print("Fetching addresses for labels B and C...")
    address_B = connection.getaddressesbylabel("B")
    address_C = connection.getaddressesbylabel("C")

    if address_B:
        address_B = list(address_B.keys())[0]
    else:
        address_B = connection.getnewaddress("B", "legacy")
    if address_C:
        address_C = list(address_C.keys())[0]
    else:
        address_C = connection.getnewaddress("C", "legacy")
    
    print(f"Address B: {address_B}")
    print(f"Address C: {address_C}")

    separator()
    print("Fetching UTXO list for Address B...")
    utxos_B = connection.listunspent(0, 9999999, [address_B])
    if not utxos_B:
        print(f"No UTXO found for address B: {address_B}")
        return

    utxo_B = utxos_B[0]
    print(f"UTXO of B:")
    print(f"  TXID: {utxo_B['txid']}")
    print(f"  Vout: {utxo_B['vout']}")
    print(f"  Amount: {utxo_B['amount']} BTC")

    fee = Decimal('0.0001')
    max_amount = Decimal(str(utxo_B["amount"])) - fee
    amount = input_amount(max_amount, address_C)

    separator()
    print("Creating the transaction from B to C...")
    inputs = [{"txid": utxo_B["txid"], "vout": utxo_B["vout"]}]
    outputs = {
        address_C: amount,
        address_B: Decimal(str(utxo_B["amount"])) - amount - fee
    }
    raw_tx = connection.createrawtransaction(inputs, outputs)
    print("Unsigned raw transaction hex:")
    print(raw_tx)

    separator()
    print("Signing the transaction from B to C...")
    signed_tx = connection.signrawtransactionwithwallet(raw_tx)
    tx_size = len(signed_tx["hex"]) // 2  
    txid_B_to_C = connection.sendrawtransaction(signed_tx["hex"])
    print(f"Transaction ID (B → C): {txid_B_to_C}")
    print(f"Transaction size: {tx_size} vbytes")

    separator()
    print("Decoding raw transaction to extract the response script for UTXO of B...")
    decoded_B_to_C = connection.decoderawtransaction(signed_tx["hex"])
    scriptSig = decoded_B_to_C["vin"][0]["scriptSig"]["hex"]
    scriptSig_size = len(scriptSig) // 2
    print("Extracted ScriptSig:")
    print(scriptSig)
    print(f"Script size: {scriptSig_size} vbytes")

    separator()
    print("Cleaning up: Unloading and deleting the wallet...")
    try:
        connection.unloadwallet(wallet)
        print(f"Unloaded wallet: {wallet}")
    except JSONRPCException as e:
        print(f"Error unloading wallet: {e}")


if __name__ == "__main__":
    main()
