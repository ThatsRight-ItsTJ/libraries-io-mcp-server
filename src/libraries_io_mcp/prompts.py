"""
Prompts for the Libraries.io MCP Server.

This module contains MCP prompt implementations for Libraries.io data.
"""

from __future__ import annotations

from fastmcp import FastMCP
from .client import LibrariesIOClient


def register_prompts(server: FastMCP, client: LibrariesIOClient) -> None:
    """
    Register all MCP prompts with the server.
    
    Args:
        server: FastMCP server instance
        client: LibrariesIOClient instance
    """
    
    @server.prompt()
    async def package_analysis_prompt(platform: str, name: str) -> str:
        """
        Generate a prompt for comprehensive package analysis.
        
        Args:
            platform: Package manager platform (e.g., 'npm', 'pypi')
            name: Package name
            
        Returns:
            Analysis prompt string
        """
        return f"""
        Analyze the package {name} from {platform}.
        
        Please provide a comprehensive analysis including:
        1. Package overview and description
        2. Version history and stability
        3. Dependencies and their licenses
        4. Popularity metrics (downloads, stars, etc.)
        5. Security considerations
        6. Alternative packages
        
        Use the available tools to gather detailed information about this package.
        """
    
    @server.prompt()
    async def dependency_analysis_prompt(platform: str, name: str, version: str | None = None) -> str:
        """
        Generate a prompt for dependency analysis.
        
        Args:
            platform: Package manager platform (e.g., 'npm', 'pypi')
            name: Package name
            version: Specific version (optional)
            
        Returns:
            Dependency analysis prompt string
        """
        version_info = f" version {version}" if version else ""
        return f"""
        Analyze the dependency tree for {name}{version_info} from {platform}.
        
        Please provide:
        1. Complete dependency tree visualization
        2. License compatibility analysis
        3. Security vulnerabilities in dependencies
        4. Potential update opportunities
        5. Dependency bloat analysis
        
        Use the available tools to explore the full dependency structure.
        """
    
    @server.prompt()
    async def ecosystem_exploration_prompt(platform: str, language: str | None = None) -> str:
        """
        Generate a prompt for ecosystem exploration.
        
        Args:
            platform: Package manager platform (e.g., 'npm', 'pypi')
            language: Programming language filter (optional)
            
        Returns:
            Ecosystem exploration prompt string
        """
        lang_info = f" for {language}" if language else ""
        return f"""
        Explore the {platform} ecosystem{lang_info}.
        
        Please provide:
        1. Overview of popular packages and trends
        2. Platform statistics and health metrics
        3. Emerging packages and technologies
        4. Best practices and recommendations
        
        Use the available tools to gather comprehensive ecosystem data.
        """

    @server.prompt()
    async def evaluate_package(package_name: str, platform: str = "npm") -> str:
        """
        Generate a prompt for comprehensive package evaluation.
        
        Args:
            package_name: Name of the package to evaluate
            platform: Package manager platform (default: "npm")
            
        Returns:
            Package evaluation prompt string
        """
        return f"""
        Evaluate the open source package '{package_name}' on {platform}.
        
        Please analyze:
        1. Package popularity and community adoption
        2. Maintenance status and update frequency
        3. Security considerations
        4. License and legal compliance
        5. Dependencies and potential risks
        6. Alternatives and recommendations
        
        Provide a comprehensive evaluation with recommendations.
        """

    @server.prompt()
    async def audit_dependencies(dependencies: list) -> str:
        """
        Generate a prompt for dependency audit.
        
        Args:
            dependencies: List of dependencies to audit
            
        Returns:
            Dependency audit prompt string
        """
        return f"""
        Perform a security and maintenance audit of these dependencies:
        {dependencies}
        
        For each dependency, check:
        - Security vulnerabilities
        - Maintenance status
        - License compliance
        - Outdated versions
        - Potential replacements
        
        Provide actionable recommendations for improving the dependency stack.
        """

    @server.prompt()
    async def analyze_project_health(project_name: str, platform: str = "npm") -> str:
        """
        Generate a prompt for project health analysis.
        
        Args:
            project_name: Name of the project to analyze
            platform: Package manager platform (default: "npm")
            
        Returns:
            Project health analysis prompt string
        """
        return f"""
        Analyze the overall health of project '{project_name}' on {platform}.
        
        Please provide a comprehensive health assessment including:
        1. Dependency tree analysis and complexity
        2. Security vulnerability summary
        3. License compliance overview
        4. Maintenance status of all dependencies
        5. Update opportunities and outdated packages
        6. Performance impact analysis
        7. Risk assessment and recommendations
        
        Use the available tools to gather comprehensive project data and provide
        actionable insights for improving project health.
        """

    @server.prompt()
    async def recommend_packages(
        requirements: str,
        platform: str = "npm",
        language: str | None = None,
        limit: int = 10
    ) -> str:
        """
        Generate a prompt for package recommendations.
        
        Args:
            requirements: Description of requirements or use case
            platform: Package manager platform (default: "npm")
            language: Programming language filter (optional)
            limit: Maximum number of recommendations (default: 10)
            
        Returns:
            Package recommendation prompt string
        """
        lang_info = f" for {language}" if language else ""
        return f"""
        Recommend packages on {platform}{lang_info} based on these requirements:
        {requirements}
        
        Please provide:
        1. Top {limit} recommended packages with detailed justifications
        2. Each package's key features and benefits
        3. Community adoption and popularity metrics
        4. License information and compliance considerations
        5. Maintenance status and update frequency
        6. Security considerations and vulnerability history
        7. Performance characteristics
        8. Comparison with alternatives
        
        Use the available tools to search and analyze packages that best match
        the specified requirements.
        """

    @server.prompt()
    async def migration_guide(
        package_name: str,
        current_version: str,
        target_version: str,
        platform: str = "npm"
    ) -> str:
        """
        Generate a prompt for package migration guide.
        
        Args:
            package_name: Name of the package to migrate
            current_version: Current version to migrate from
            target_version: Target version to migrate to
            platform: Package manager platform (default: "npm")
            
        Returns:
            Migration guide prompt string
        """
        return f"""
        Create a comprehensive migration guide for '{package_name}' from version
        {current_version} to {target_version} on {platform}.
        
        Please provide:
        1. Version differences and breaking changes
        2. API changes and deprecations
        3. Configuration and setup changes
        4. Migration step-by-step instructions
        5. Code examples for common changes
        6. Testing recommendations
        7. Rollback procedures
        8. Performance considerations
        9. Security implications
        10. Migration timeline and effort estimation
        
        Use the available tools to gather detailed version information and
        provide actionable migration guidance.
        """

    @server.prompt()
    async def security_assessment(
        project_name: str,
        platform: str = "npm",
        include_dependencies: bool = True
    ) -> str:
        """
        Generate a prompt for security assessment.
        
        Args:
            project_name: Name of the project to assess
            platform: Package manager platform (default: "npm")
            include_dependencies: Whether to include dependency analysis (default: True)
            
        Returns:
            Security assessment prompt string
        """
        scope = "including all dependencies" if include_dependencies else "for the main package"
        return f"""
        Perform a comprehensive security assessment for project '{project_name}'
        on {platform} {scope}.
        
        Please analyze:
        1. Known security vulnerabilities in the package(s)
        2. Dependency security risks and vulnerabilities
        3. License compliance and legal risks
        4. Outdated packages with potential security issues
        5. Supply chain security considerations
        6. Code security best practices
        7. Security rating and risk score
        8. Immediate action items and recommendations
        9. Long-term security maintenance strategy
        
        Use the available tools to gather security data and provide
        prioritized recommendations for risk mitigation.
        """

    @server.prompt()
    async def license_compliance_check(
        dependencies: list,
        policy_requirements: str = "permissive"
    ) -> str:
        """
        Generate a prompt for license compliance checking.
        
        Args:
            dependencies: List of dependencies to check
            policy_requirements: License policy requirements (default: "permissive")
            
        Returns:
            License compliance check prompt string
        """
        return f"""
        Perform a comprehensive license compliance check for these dependencies:
        {dependencies}
        
        Based on the policy requirements: {policy_requirements}
        
        Please analyze:
        1. License compatibility matrix
        2. License obligations and restrictions
        3. Commercial use considerations
        4. Attribution and notice requirements
        5. Patent clauses and implications
        6. Copyleft vs permissive license analysis
        7. Risk assessment for each license
        8. Compliance gaps and violations
        9. Recommended license alternatives
        10. Legal review recommendations
        
        Use the available tools to gather license information and provide
        actionable compliance guidance.
        """

    @server.prompt()
    async def maintenance_status_report(
        project_name: str,
        platform: str = "npm",
        time_period: str = "6 months"
    ) -> str:
        """
        Generate a prompt for maintenance status report.
        
        Args:
            project_name: Name of the project to analyze
            platform: Package manager platform (default: "npm")
            time_period: Time period for analysis (default: "6 months")
            
        Returns:
            Maintenance status report prompt string
        """
        return f"""
        Generate a comprehensive maintenance status report for project '{project_name}'
        on {platform} over the last {time_period}.
        
        Please provide:
        1. Update frequency and release cadence
        2. Version stability and changelog analysis
        3. Community engagement metrics
        4. Issue resolution rate and response time
        5. Pull request activity and contribution patterns
        6. Maintenance burden assessment
        7. Long-term sustainability indicators
        8. Risk factors and warning signs
        9. Maintenance recommendations
        10. Future outlook and predictions
        
        Use the available tools to gather maintenance data and provide
        insights into the project's long-term viability.
        """


__all__ = [
    "register_prompts",
    "package_analysis_prompt",
    "dependency_analysis_prompt",
    "ecosystem_exploration_prompt",
    "evaluate_package",
    "audit_dependencies",
    "analyze_project_health",
    "recommend_packages",
    "migration_guide",
    "security_assessment",
    "license_compliance_check",
    "maintenance_status_report"
]