import base64
import otp_migration_pb2  # gerado no passo anterior

def decode_otp_migration(encoded):
    decoded = base64.urlsafe_b64decode(encoded)
    payload = otp_migration_pb2.MigrationPayload()
    payload.ParseFromString(decoded)
    return payload

def main():
    encoded = "Ck0KIEI4QzJGRUI4ODQ2RDRDRURBM0Q3NDk3MjhFQ0REMzlDEgdDcmVmaXNhGgUydGVjaCABKAEwAkITNjdjYmFhMTc0NzY3NzAxODI1MhACGAEgAA=="
    payload = decode_otp_migration(encoded)

    for i, otp in enumerate(payload.otp_parameters, 1):
        print(f"\n--- Conta {i} ---")
        print("Issuer:", otp.issuer)
        print("Name:", otp.name)
        print("Secret (Base32):", base64.b32encode(otp.secret).decode())
        print("Algorithm:", otp.algorithm)
        print("Digits:", otp.digits)
        print("Type:", otp.type)
        print("Counter:", otp.counter)

if __name__ == "__main__":
    main()
