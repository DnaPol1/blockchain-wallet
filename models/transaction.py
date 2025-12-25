from pydantic import BaseModel, Field

class SignedTransaction(BaseModel):
    sender: str = Field(..., description="Public key / address отправителя")
    receiver: str = Field(..., description="Адрес получателя")
    amount: float = Field(..., gt=0)
    signature: str = Field(..., description="ECDSA signature (hex)")