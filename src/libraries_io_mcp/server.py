"""
Libraries.io MCP Server implementation.

This module contains the main server implementation for the Libraries.io MCP Server.
"""

import os
import logging
import asyncio
from typing import Optional
from dotenv import load_dotenv

from fastmcp import FastMCP
from .client import LibrariesIOClient
from .tools import register_tools
from .resources import register_resources
from .prompts import register_prompts


# Load environment variables
load_dotenv()


class LibrariesIOServer:
    """
    Main server class for the Libraries.io MCP Server.
    
    This class coordinates the FastMCP server with the LibrariesIOClient
    and registers all tools, resources, and prompts.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        host: str = "0.0.0.0",
        port: int = 8000,
        log_level: str = "INFO"
    ):
        """
        Initialize the Libraries.io MCP Server.
        
        Args:
            api_key: API key for Libraries.io API (can also be set via LIBRARIES_IO_API_KEY env var)
            host: Host address to bind the server to
            port: Port to bind the server to
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.api_key = api_key or os.getenv("LIBRARIES_IO_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key is required. Set LIBRARIES_IO_API_KEY environment variable "
                "or pass api_key parameter."
            )
        
        self.host = host
        self.port = port
        self.log_level = log_level
        
        # Initialize logger
        self.logger = self._setup_logger()
        
        # Initialize FastMCP server
        self.server = FastMCP(
            name="Libraries.io MCP Server",
            version="0.1.0",
            description="A Model Context Protocol server for interacting with the Libraries.io API"
        )
        
        # Initialize client
        self.client = LibrariesIOClient(
            api_key=self.api_key,
            logger=self.logger
        )
        
        self.logger.info("Libraries.io MCP Server initialized")
    
    def _setup_logger(self) -> logging.Logger:
        """Set up logging configuration."""
        logger = logging.getLogger("libraries_io_mcp")
        logger.setLevel(getattr(logging, self.log_level.upper()))
        
        # Create console handler
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        
        # Add handler to logger
        if not logger.handlers:
            logger.addHandler(handler)
        
        return logger
    
    def register_tools(self) -> None:
        """Register all MCP tools with the server."""
        try:
            register_tools(self.server, self.client)
            self.logger.info("Tools registered successfully")
        except Exception as e:
            self.logger.error(f"Failed to register tools: {e}")
            raise
    
    def register_resources(self) -> None:
        """Register all MCP resources with the server."""
        try:
            register_resources(self.server, self.client)
            self.logger.info("Resources registered successfully")
        except Exception as e:
            self.logger.error(f"Failed to register resources: {e}")
            raise
    
    def register_prompts(self) -> None:
        """Register all MCP prompts with the server."""
        try:
            register_prompts(self.server, self.client)
            self.logger.info("Prompts registered successfully")
        except Exception as e:
            self.logger.error(f"Failed to register prompts: {e}")
            raise
    
    def register_all(self) -> None:
        """Register all tools, resources, and prompts."""
        self.register_tools()
        self.register_resources()
        self.register_prompts()
        self.logger.info("All components registered successfully")
    
    async def start(self) -> None:
        """Start the MCP server."""
        try:
            self.logger.info(f"Starting server on {self.host}:{self.port}")
            await self.server.serve(host=self.host, port=self.port)
        except Exception as e:
            self.logger.error(f"Failed to start server: {e}")
            raise
    
    async def run(self) -> None:
        """Run the server with all components registered."""
        self.register_all()
        await self.start()


def create_server(
    api_key: Optional[str] = None,
    host: str = "0.0.0.0",
    port: int = 8000,
    log_level: str = "INFO"
) -> LibrariesIOServer:
    """
    Create and configure a LibrariesIOServer instance.
    
    Args:
        api_key: API key for Libraries.io API
        host: Host address to bind the server to
        port: Port to bind the server to
        log_level: Logging level
        
    Returns:
        Configured LibrariesIOServer instance
    """
    return LibrariesIOServer(
        api_key=api_key,
        host=host,
        port=port,
        log_level=log_level
    )


async def main() -> None:
    """Main entry point for the server."""
    try:
        # Create server instance
        server = create_server()
        
        # Run the server
        await server.run()
    except KeyboardInterrupt:
        print("\nServer shutting down...")
    except Exception as e:
        print(f"Server error: {e}")
        raise


if __name__ == "__main__":
    # Run the server when executed directly
    asyncio.run(main())