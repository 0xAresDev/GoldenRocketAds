from .models import Servers

def IsServerOwner(request):
    data = request.data
    servers = Servers.objects.filter(guild=data.get("guild"))
    if len(servers) > 0:
        if int(servers[0].owner) == int(data.get("sender")):
            return True
    return False
