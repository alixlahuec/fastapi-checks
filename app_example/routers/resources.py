from typing import Annotated
from fastapi import APIRouter, Depends

from app_example import Config

from fastapi_checks.decorators import mark


class RouterDep:
    def __init__(self, *, some_param: int):
        self.some_param = some_param

    def __call__(self, config: Config = Depends()):
        return config.some_api_key == self.some_param


router = APIRouter(
    prefix="/resource",
    tags=["resource"],
    dependencies=[Depends(RouterDep(some_param=666))],
)


class ClassDep:
    def __init__(self, *, some_param: int):
        self.some_param = some_param

    def __call__(self, config: Config = Depends()):
        return config.some_api_key == self.some_param


@mark("misc")
def some_dependency(num: int = Depends(ClassDep(some_param=123))) -> bool:
    return num == 999


@mark("tenant_enforced")
def with_tenant_required(num: int = Depends(ClassDep(some_param=123))) -> bool:
    return num == 999


HasTenant = Annotated[bool, Depends(with_tenant_required)]

AnnotatedDep = Annotated[bool, Depends(some_dependency)]


@router.get(
    "/0.1/{resource_id}",
    name="Get resource",
    deprecated=True,
    openapi_extra={"security": [{"HTTPBearer": ["myapp:some_scope"]}]},
)
@router.get("/{resource_id}", name="Get resource", dependencies=[Depends(some_dependency)])
def get_resource(
    arg1: AnnotatedDep,
    config: Config = Depends(),
    arg2: int = Depends(ClassDep(some_param=17)),
) -> list[str]:
    return ["some_string"]


@router.delete(
    "/{resource_id}",
    name="Delete resource",
)
def delete_resource(has_tenant: HasTenant) -> bool:
    return has_tenant
