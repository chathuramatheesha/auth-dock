from dataclasses import fields, is_dataclass, asdict


async def check_dto_is_dataclass(dto):
    if not is_dataclass(dto):
        raise ValueError(f"{dto} Must be a dataclass")


async def db_to_dto(db_model, dto):
    await check_dto_is_dataclass(dto)

    model_dict = db_model.__dict__
    dto_data = {
        field.name: model_dict.get(field.name)
        for field in fields(dto)
        if field.name in model_dict
    }
    return dto(**dto_data)


async def pydantic_to_dto(pydantic_model, dto):
    await check_dto_is_dataclass(dto)
    return dto(**pydantic_model.model_dump())


async def dto_to_update_db(dto) -> dict:
    await check_dto_is_dataclass(dto)
    filtered_fields = {k: v for k, v in {**asdict(dto)}.items() if v is not None}
    return filtered_fields


# Convert DTO -> Pydantic
async def dto_to_pydantic(pydantic_model, dto):
    await check_dto_is_dataclass(dto)
    return pydantic_model.model_validate(dto)


async def dto_to_dto(source_dto, dto):
    await check_dto_is_dataclass(source_dto)
    await check_dto_is_dataclass(dto)

    source_dto_dict = asdict(source_dto)
    target_fields = {f.name for f in fields(dto)}
    filtered_data = {k: v for k, v in source_dto_dict.items() if k in target_fields}
    return dto(**filtered_data)


async def is_dto_empty(dto) -> bool:
    return not any(value is not None for value in asdict(dto).values())
