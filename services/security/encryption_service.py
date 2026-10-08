# For production, replace this helper with a managed KMS/envelope-encryption service.
# The prototype avoids pretending that application-level reversible encryption is a
# substitute for TLS, database encryption-at-rest, key management and access controls.
import hashlib
def pseudonym(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()
