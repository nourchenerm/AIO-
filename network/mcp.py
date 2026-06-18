import asyncio
import logging
import sys
from pathlib import Path

class MCPProtocol:
    
    
    def __init__(self, config):
        # config: Configuration contenant 'mcp_servers'
        
        self.config = config
        self.logger = logging.getLogger("network.mcp_protocol")
        self.mcp_servers = config.get("mcp_servers", {})
        
        self.tool_manager = None
        self.available_tools = []
        self.is_connected = False
        self.loop = None
        
    
    def connect(self):
        try:
            self.loop = asyncio.new_event_loop()
            
            self.loop.run_until_complete(asyncio.wait_for(self._async_connect(), timeout=10.0))
            
            self.is_connected = True
            self.logger.info("✅ MCP Protocol connected")
        except asyncio.TimeoutError:
            self.logger.error("❌ MCP Connection timed out! Check if pneumatics.py is crashing.")
        except Exception as e:
            self.logger.error(f"❌ MCP connection failed: {e}")

    
    async def _async_connect(self):
        """
        Initialisation asynchrone des connexions MCP
        """
        try:
            project_root = Path(__file__).parent.parent
            if str(project_root) not in sys.path:
                sys.path.insert(0, str(project_root))
            
            from functions.seat_agent.utils.tools_manager import ToolManager
            
            self.tool_manager = ToolManager(self.mcp_servers)
            self.tool_manager.context = {}
            
            await self.tool_manager.initialize()
            
            self.available_tools = await self.tool_manager.discover_all() 

            
            if len(self.available_tools) == 0:
                self.logger.warning("⚠️  No tools discovered")
            else:
                for server_name, server_info in self.tool_manager.sessions.items():
                    tool_count = len(server_info.get("tools", []))
            
        except Exception as e:
            self.logger.error(f"❌ Async connection error: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            raise
    
    def disconnect(self):
        
        if not self.is_connected:
            return
        
        try:
            self.logger.info("🔌 Disconnecting MCP servers...")
            
            if self.tool_manager and self.loop:
                # Créer une nouvelle event loop si nécessaire
                if self.loop.is_closed():
                    self.loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(self.loop)
                
                # Exécuter le cleanup async
                self.loop.run_until_complete(self.tool_manager.cleanup())
            
            if self.loop and not self.loop.is_closed():
                self.loop.close()
            
            self.is_connected = False
            self.logger.info("✅ MCP Protocol disconnected")
            
        except Exception as e:
            self.logger.error(f"❌ Disconnect error: {e}")
    
    def call_tool(self, tool_name: str, arguments: dict):
        
        if not self.is_connected or not self.tool_manager:
            raise RuntimeError("MCP not connected. Call connect() first.")
        
        # Vérifier si la loop est toujours ouverte
        if self.loop.is_closed():
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
        
        # Exécuter l'appel async de manière synchrone
        return self.loop.run_until_complete(
            self.tool_manager.call_tool(tool_name, arguments)
        )
    
    def get_available_tools(self):
       
        return self.available_tools
    
    def is_ready(self):
       
        return self.is_connected and len(self.available_tools) > 0