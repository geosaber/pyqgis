"""
Enhanced Trend Surface Analysis Plugin for QGIS
"""

def classFactory(iface):
    from .enhanced_trend_surface import EnhancedTrendSurfacePlugin
    return EnhancedTrendSurfacePlugin(iface)
