# Bitcoin Scripting

## Team Information

**Team Name:** xyz  
**Team Members:**

- Kunal Gourv (230002036)
- Kumar Ayaman (230001044)
- Cheepati Gireesh Kumar Reddy (230005013)

## Project Overview

This repository provides a Python implementation for creating and validating Bitcoin transactions. It compares Legacy (P2PKH) and SegWit (P2SH-P2WPKH) address formats, highlighting differences in transaction sizes and structural characteristics.

## Implementation Process

Our code executes the following sequence:

1. **Wallet Setup**: Creates a new wallet (or loads an existing one) and generates three addresses: A, B, and C.

2. **Initial Funding**: Mines blocks to fund address A, then displays the UTXO (Unspent Transaction Output) balance of A.

3. **Transaction Amount**: Prompts the user for a transfer amount from A to B, ensuring:

   ```
   0 < Amount ≤ UTXO(A) - Mining fee
   ```

4. **Transaction Creation (A → B)**:

   - Creates a raw transaction transferring coins from A to B
   - Decodes the transaction to extract the challenge script (ScriptPubKey)
   - Displays transaction size in virtual bytes (vbytes)

5. **Transaction Signing and Broadcasting**:

   - Signs the A → B transaction using A's private key
   - Broadcasts it to the network
   - Displays the transaction ID and size

6. **UTXO Verification**: Fetches and displays B's UTXO details from the A → B transaction

7. **Second Transaction (B → C)**:

   - Creates a new transaction from B to C using B's UTXO balance
   - Follows the same procedure as the A → B transaction
   - Displays transaction ID and size

8. **Script Extraction**: Decodes the B → C transaction to extract the response script (ScriptSig) and displays its size

9. **Cleanup**: Unloads the wallet when finished

## Configuration Options

### 1. User Credentials

Default credentials in bitcoin.conf are:

- Username: `xyz`
- Password: `xyz`

To modify these settings:

- Update the `rpcuser` and `rpcpassword` fields in the bitcoin.conf file
- Change the corresponding credentials in the `get_rpc_connection()` function in the Python code

### 2. Block Mining Configuration

By default, the program mines 101 blocks to fund address A. This can be adjusted by modifying the line:

```python
connection.generatetoaddress(101, address_A)
```

### 3. Transaction Fee Adjustment

The default transaction fee is 0.0001 BTC/kB for both A → B and B → C transactions. Modify the `fee` variable in the code to adjust this amount.

## Setup and Execution Instructions

### Prerequisites

- Bitcoin Core software
- python-bitcoinrpc library

### Installation

1. Install and configure bitcoind on your system
2. Install the required Python library:
   ```
   pip install python-bitcoinrpc
   ```

### Configuration

1. Navigate to Bitcoin configuration directory:
   ```
   C:\Users\<username>\AppData\Roaming\Bitcoin
   ```
   (Replace `<username>` with your actual username)
2. Copy the provided bitcoin.conf file to this directory

### Running the Application

1. Launch Bitcoin Core in regtest mode:

   ```
   cd "C:\Program Files\Bitcoin\daemon"
   bitcoind.exe -regtest
   ```

2. Run Legacy transaction scripts:

   - Execute `legacy_xyz.py` to create the A → B transaction and extract ScriptPubKey
   - Execute `legacy1_xyz.py` to create the B → C transaction and extract ScriptSig

3. Before running SegWit tests:

   - Close the Command Prompt
   - Delete the regtest directory from the Bitcoin directory
   - Restart Bitcoin Core in regtest mode as in step 1

4. Run SegWit transaction script:
   - Execute `segwit.py` to create similar transactions using SegWit address format

## Script Validation

Connect to the Bitcoin Debugger server:

```
ssh guest@10.206.4.201
```

Password: `root1234`

Validate extracted scripts with:

```
btcdeb -v '<ScriptSig><ScriptPubKey>'
```

Replace `<ScriptSig>` with the response script and `<ScriptPubKey>` with the challenge script, with no spaces between them.

**Validation Results:**

- "valid script" indicates challenge and response scripts are valid
- "invalid script" indicates the scripts are invalid
