# -*- test-case-name: miru.test.test_components -*-
# Copyright (c) 2008 Drew Smathers.
# See LICENSE for details


class AlreadyRegistered(Exception):
    """Raised if we try to register more than on utility under the
    same interface.
    """

_global_utility_registry = {}

def registerUtility(iface, provider, override=False):
    """Register a singleton provider of an interface.

    @param iface: The Interface to register utility under
    @param provider: A provider of the interface
    @param override: If already registered, override previous registration
    @type  override: C{bool}
    """
    if _global_utility_registry.has_key(iface) and not override:
        raise AlreadyRegistered, 'Utility already registered for %r' % iface
    _global_utility_registry[iface] = provider

def destroyUtility(iface):
    """Unregister a utility providing iface (if registered)

    @param iface: The Interface a utility might be registered under
    """
    if _global_utility_registry.has_key(iface):
        del _global_utility_registry[iface]

def getUtility(iface):
    """Get the registered utility provided by interface.

    @param iface: The Interface the utility must be registered under
    @return: The registered utility
    """
    return _global_utility_registry[iface]



