from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, Field, field_validator

app = FastAPI()

BALANCE = {}

class OperationRequest(BaseModel):
    wallet_name: str = Field(..., max_length=127)
    amount: float
    description: str | None = Field(None, max_length=255)

    @field_validator('amount')
    def amount_must_be_positive(cls, v: float) -> float:
        # Проверяем что значение больше нуля
        if v <= 0:
            raise ValueError("Amount must be positive")
        return v
    
    @field_validator('wallet_name')
    def wallet_name_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Wallet name cannot be empty")
        return v


class CreateWalletRequest(BaseModel):
    name: str = Field(..., max_length=127)
    initial_balance: float = 0
    @field_validator('name')
    def name_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Wallet name cannot be empty")
        return v
    
    @field_validator('initial_balance')
    def balance_not_negative(cls, v: float) -> float:
        # Проверяем что значение больше нуля
        if v < 0:
            raise ValueError("Initial balance cannot be negative")
        return v


@app.get("/health")
def health_check():
    return Response(content="OK", media_type="text/plain")

@app.get("/balance")
def get_balance(wallet_name: str | None = None):
    # Если имя кошелька не указано - считаем общий баланс
    if wallet_name is None:
        return {"total_balance": sum(BALANCE.values())}
    # Проверяем, существует ли запрашиваемый кошелек
    if wallet_name not in BALANCE:
        raise HTTPException(
            status_code=404,
            detail=f"Wallet '{wallet_name}' not found"
        )
    # Возвращаем баланс конкретного кошелька
    return {"wallet": wallet_name, "balance": BALANCE[wallet_name]}


@app.post("/wallets")
def create_wallet(wallet: CreateWalletRequest):
    # Проверяем, не существует ли уже такой кошелек
    if wallet.name in BALANCE:
        raise HTTPException(
            # Если кошелек уже есть - возвращаем ошибку 404
            status_code=400,
            detail=f"Wallet '{wallet.name}' already exists"
        )
    # Создаем новый кошелек с начальным балансом
    BALANCE[wallet.name] = wallet.initial_balance
    # Возвращаем информацию о созданном кошельке
    return {
        "message": f"Wallet '{wallet.name}' created",
        "wallet": wallet.name,
        "balance": BALANCE[wallet.name]
    }


@app.post("/operations/income")
def add_income(operation: OperationRequest):
    # Проверяем существует ли кошелек
    if operation.wallet_name not in BALANCE:
        raise HTTPException(
            status_code=404,
            detail=f"Wallet '{operation.wallet_name}' not found"
        )
    # Проверка на положительность суммы реализована в модели

    # Добавляем доход к балансу кошелька
    BALANCE[operation.wallet_name] += operation.amount
    # Возвращаем информацию об операции
    return {
        "message": "Income added",
        "wallet": operation.wallet_name,
        "amount": operation.amount,
        "description": operation.description,
        "new_balance": BALANCE[operation.wallet_name]
    }


@app.post("/operations/expense")
def add_expense(operation: OperationRequest):
    # Проверяем существует ли кошелек
    if operation.wallet_name not in BALANCE:
        raise HTTPException(
            status_code=404,
            detail=f"Wallet '{operation.wallet_name}' not found"
        )
    # Проверка на положительность суммы реализована в модели
    
    # Проверяем достаточно ли средств в кошельке
    if BALANCE[operation.wallet_name] < operation.amount:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient funds. Available: {BALANCE[operation.wallet_name]}"
        )
    # Вычитаем расход из баланса кошелька
    BALANCE[operation.wallet_name] -= operation.amount
    # Возвращаем информацию об операции
    return {
        "message": "Expense added",
        "wallet": operation.wallet_name,
        "amount": operation.amount,
        "description": operation.description,
        "new_balance": BALANCE[operation.wallet_name]
    }