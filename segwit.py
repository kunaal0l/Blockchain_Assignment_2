import bitcoinrpc.authproxy as authproxy
import hashlib


def separator():
    """Print a line separator for better console readability."""
    print("-" * 60)


def prompt_for_amount(max_value, prompt_msg="Enter amount: "):
    """Request a valid numeric amount from the user that does not exceed the maximum available."""
    while True:
        try:
            amount = float(input(f"{prompt_msg} (max {max_value:.8f} BTC): "))
            if amount <= 0:
                print("The amount must be greater than zero.")
            elif amount > max_value:
                print(
                    "The entered amount is more than available funds. Try a lower value."
                )
            else:
                return amount
        except ValueError:
            print("Error: please enter a valid numeric value.")


def compute_script_stats(hex_script):
    """
    Compute the script's byte size, weight, and virtual size.
    For non-witness data: weight = byte_size * 4, and virtual size equals byte_size.
    """
    script_bytes = bytes.fromhex(hex_script)
    byte_size = len(script_bytes)
    weight = byte_size * 4
    vsize = byte_size
    return byte_size, weight, vsize


def hash160(data):
    """Compute hash160 (RIPEMD160(SHA256(data))) as used in Bitcoin."""
    sha256 = hashlib.sha256(data).digest()
    ripemd160 = hashlib.new("ripemd160")
    ripemd160.update(sha256)
    return ripemd160.digest()


rpc_username = "xyz"
rpc_password = "xyz"
base_rpc_url = f"http://{rpc_username}:{rpc_password}@127.0.0.1:18443"
wallet_id = "Team_xyz"

separator()
print("Initializing wallet...")

rpc_conn = authproxy.AuthServiceProxy(base_rpc_url)
try:
    rpc_conn.loadwallet(wallet_id)
    print(f"Wallet '{wallet_id}' loaded successfully.")
except authproxy.JSONRPCException as err:
    if err.error["code"] == -35:
        print(f"Wallet '{wallet_id}' is already active.")
    elif err.error["code"] == -18:
        print(f"Wallet '{wallet_id}' not found; creating it now.")
        rpc_conn.createwallet(wallet_id)
        rpc_conn = authproxy.AuthServiceProxy(f"{base_rpc_url}/wallet/{wallet_id}")
        mining_addr = rpc_conn.getnewaddress()
        rpc_conn.generatetoaddress(101, mining_addr)
    else:
        raise

rpc_conn = authproxy.AuthServiceProxy(f"{base_rpc_url}/wallet/{wallet_id}")

rpc_conn.settxfee(0.0001)
separator()
print("Fee set to 0.0001 BTC/kB")

separator()
print("Generating P2SH-SegWit addresses A', B', and C'...")

addr_A_prime = rpc_conn.getnewaddress("A'", "p2sh-segwit")
addr_B_prime = rpc_conn.getnewaddress("B'", "p2sh-segwit")
addr_C_prime = rpc_conn.getnewaddress("C'", "p2sh-segwit")

print(f"Address A': {addr_A_prime}")
print(f"Address B': {addr_B_prime}")
print(f"Address C': {addr_C_prime}")

separator()
print("Funding Address A' with 10 BTC using sendtoaddress...")
txid_fund_A = rpc_conn.sendtoaddress(addr_A_prime, 10)
print(f"Funding transaction ID: {txid_fund_A}")
rpc_conn.generatetoaddress(1, rpc_conn.getnewaddress())
print("Address A' funded with 10 BTC and confirmed.")

separator()
print("Creating transaction from A' to B'...")

utxos_A = rpc_conn.listunspent(1, 9999999, [addr_A_prime])
if not utxos_A:
    raise Exception("No UTXO available for A'")
utxo_A = utxos_A[0]
balance_A = float(utxo_A["amount"])
print(f"Balance in A': {balance_A:.8f} BTC")

transfer_amt_AB = prompt_for_amount(balance_A, "Enter amount to transfer from A' to B'")
fee_estimate = 0.0001
change_amt = balance_A - transfer_amt_AB - fee_estimate
if change_amt < 0:
    raise Exception("Insufficient funds for transaction plus fee")

raw_tx_AB = rpc_conn.createrawtransaction(
    [{"txid": utxo_A["txid"], "vout": utxo_A["vout"]}],
    {addr_B_prime: transfer_amt_AB, addr_A_prime: change_amt},
)

decoded_tx_AB = rpc_conn.decoderawtransaction(raw_tx_AB)
challenge_script = decoded_tx_AB["vout"][0]["scriptPubKey"]["hex"]

decoded_challenge = rpc_conn.decodescript(challenge_script)
print("Decoded Challenge Script:")
print(decoded_challenge)
print(f"'scriptPubKey': {challenge_script}")

print("Signing the transaction A → B")
signed_tx_AB = rpc_conn.signrawtransactionwithwallet(raw_tx_AB)
txid_AB = rpc_conn.sendrawtransaction(signed_tx_AB["hex"])
rpc_conn.generatetoaddress(1, rpc_conn.getnewaddress())
print(f"Transaction A' -> B' broadcasted with ID: {txid_AB}")

separator()
print("Creating transaction from B' to C'...")

utxos_B = rpc_conn.listunspent(1, 9999999, [addr_B_prime])
if not utxos_B:
    raise Exception("No UTXO available for B'")
utxo_B = utxos_B[0]
balance_B = float(utxo_B["amount"])
print(
    f"UTXO used for transaction from B' to C': txid={utxo_B['txid']}, vout={utxo_B['vout']}, amount={utxo_B['amount']} BTC"
)
print(f"Balance in B': {balance_B:.8f} BTC")

transfer_amt_BC = prompt_for_amount(balance_B, "Enter amount to transfer from B' to C'")
change_amt_BC = balance_B - transfer_amt_BC - fee_estimate
if change_amt_BC < 0:
    raise Exception("Insufficient funds for transaction plus fee")

raw_tx_BC = rpc_conn.createrawtransaction(
    [{"txid": utxo_B["txid"], "vout": utxo_B["vout"]}],
    {addr_C_prime: transfer_amt_BC, addr_B_prime: change_amt_BC},
)

print("Signing the transaction B → C")
signed_tx_BC = rpc_conn.signrawtransactionwithwallet(raw_tx_BC)
txid_BC = rpc_conn.sendrawtransaction(signed_tx_BC["hex"])
rpc_conn.generatetoaddress(1, rpc_conn.getnewaddress())
print(f"Transaction B' -> C' broadcasted with ID: {txid_BC}")

decoded_tx_BC = rpc_conn.decoderawtransaction(signed_tx_BC["hex"])
redeem_script_hex = decoded_tx_BC["vin"][0]["scriptSig"]["hex"]
witness_data = decoded_tx_BC["vin"][0].get("txinwitness", [])
print(f"Witness Data: {witness_data}")
decoded_redeem = rpc_conn.decodescript(redeem_script_hex)
separator()
print("Decoded Redeem Script:")
print(decoded_redeem)
print(f"'ScriptSig': {redeem_script_hex}")


separator()
print("Unloading wallet...")
rpc_admin = authproxy.AuthServiceProxy(base_rpc_url)
rpc_admin.unloadwallet(wallet_id)
print(f"Wallet '{wallet_id}' unloaded.")
separator()
