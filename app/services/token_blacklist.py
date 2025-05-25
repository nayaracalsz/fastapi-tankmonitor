from firebase_admin import firestore

db = firestore.client()


def add_token_to_blacklist(jti: str, exp: int):
    db.collection("blacklisted_tokens").document(jti).set(
        {"jti": jti, "exp": exp, "created_at": firestore.SERVER_TIMESTAMP}
    )


def is_token_blacklisted(jti: str) -> bool:
    doc = db.collection("blacklisted_tokens").document(jti).get()
    return doc.exists
