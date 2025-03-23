from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from decimal import Decimal, InvalidOperation

def separator():
    """Print a line separator for better console readability."""
    print("-" * 60)

def input_amount(max_amount: Decimal, address_B: str) -> Decimal:
    while True:
        try:
            amount = Decimal(input(f"Enter the amount to send from A to B (max {max_amount} BTC): "))
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
    connection = AuthServiceProxy(f"http://{user}:{password}@127.0.0.1:18443")
    wallet = "Team_xyz"

    separator()
    print("Initializing Legacy Wallet...")

    try:
        connection.loadwallet(wallet)
        print(f"Loaded wallet: {wallet}")
    except JSONRPCException:
        connection.createwallet(wallet)
        print(f"Created wallet: {wallet}")

    connection = AuthServiceProxy(f"http://{user}:{password}@127.0.0.1:18443/wallet/{wallet}")

    address_A = connection.getnewaddress("A", "legacy")
    address_B = connection.getnewaddress("B", "legacy")
    address_C = connection.getnewaddress("C", "legacy")

    separator()
    print("Legacy Addresses:")
    print(f"A: {address_A}")
    print(f"B: {address_B}")
    print(f"C: {address_C}")

    separator()
    print("Some initial blocks are being mined to fund address A...")
    connection.generatetoaddress(101, address_A)
    balance_A = connection.getbalance()
    print(f"Balance of A: {balance_A} BTC")

    utxo_list = connection.listunspent(1, 9999999, [address_A])
    if not utxo_list:
        raise Exception("No UTXO found for Address A after mining.")
    utxo_A = utxo_list[0]
    print(f"UTXO of A: {utxo_A['amount']} BTC")

    fee = Decimal('0.0001')
    max_amount = utxo_A["amount"] - fee

    separator()
    amount = input_amount(max_amount, address_B)

    separator()
    print("Creating a raw transaction from A to B")
    inputs = [{"txid": utxo_A["txid"], "vout": utxo_A["vout"]}]
    outputs = {
        address_B: amount,
        address_A: utxo_A["amount"] - amount - fee
    }
    raw_tx = connection.createrawtransaction(inputs, outputs)
    print("Unsigned raw transaction hex:")
    print(raw_tx)

    separator()
    print("The raw transaction is being decoded to extract the challenge script for the UTXO of B...")
    decoded_tx = connection.decoderawtransaction(raw_tx)
    scriptPubKey = decoded_tx["vout"][0]["scriptPubKey"]["hex"]
    script_size = len(scriptPubKey) // 2  # 1 byte = 2 hex chars
    print(f"Extracted ScriptPubKey: {scriptPubKey}")
    print(f"Script size: {script_size} bytes")

    separator()
    print("Signing the transaction A → B...")
    signed_tx = connection.signrawtransactionwithwallet(raw_tx)
    print("Signed transaction hex:")
    print(signed_tx['hex'])

    separator()
    print("Broadcasting the transaction A → B...")
    txid_A_to_B = connection.sendrawtransaction(signed_tx["hex"])
    tx_size = len(signed_tx["hex"]) // 2
    print(f"Transaction ID (A → B): {txid_A_to_B}")
    print(f"Transaction size: {tx_size} bytes")

    # Wrap up
    try:
        separator()
        print("Unloading wallet...")
        connection.unloadwallet(wallet)
        print(f"Unloaded wallet: {wallet}")
    except JSONRPCException as e:
        print(f"Error unloading wallet: {e}")

if __name__ == "__main__":
    main()
