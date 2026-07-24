"""Providers : chaque source de données implémente une interface simple.

Tous les providers renvoient TOUJOURS un résultat exploitable : en cas
d'absence de clé API ou d'erreur réseau, ils basculent sur une source
gratuite ou sur des valeurs de secours neutres (jamais d'exception qui
casse le pipeline temps réel).
"""
