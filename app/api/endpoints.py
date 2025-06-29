import importlib
import pkgutil
from fastapi import APIRouter, Depends
from app.services.service import Service

router = APIRouter()

def register_services(router: APIRouter):
    import app.services

    for _, module_name, _ in pkgutil.iter_modules(app.services.__path__):
        module = importlib.import_module(f"app.services.{module_name}")
        svc = getattr(module, "service", None)

        if svc and isinstance(svc, Service):
            route_path = f"/{module_name}"

            if svc.query_model:
                Model = svc.query_model

                def make_endpoint(service_instance, model_class):
                    async def endpoint(params: model_class = Depends()):
                        return service_instance.get(**params.model_dump(by_alias=False))
                    return endpoint

                router.get(route_path)(make_endpoint(svc, Model))
            else:
                def make_simple_endpoint(service_instance):
                    async def endpoint():
                        return service_instance.get()
                    return endpoint
                
                router.get(route_path)(make_simple_endpoint(svc))

register_services(router)
