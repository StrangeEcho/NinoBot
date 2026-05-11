from typing import Optional

import aiohttp


class Project:
    def __init__(
        self,
        *,
        id: str,
        name: str,
        framework: Optional[str],
        production_domain: Optional[list[str]],
        is_deployed: bool,
        is_live: bool,
    ) -> None:
        self.id = id
        self.name = name
        self.framework = framework
        self.production_domain = production_domain

        self.is_deployed = is_deployed
        self.is_live = is_live


class VercelClient:
    BASE_URL = "https://api.vercel.com"

    def __init__(
        self,
        token: str,
        *,
        team_id: str | None = None,
    ) -> None:
        self.team_id = team_id

        self.headers = {
            "Authorization": (f"Bearer {token}"),
        }

    async def get_projects(
        self,
    ) -> list[Project]:
        params = {}

        if self.team_id:
            params["teamId"] = self.team_id

        async with aiohttp.ClientSession(headers=self.headers) as session:
            # Fetch projects
            async with session.get(
                f"{self.BASE_URL}/v9/projects",
                params=params,
            ) as response:
                response.raise_for_status()

                project_data = await response.json()

            projects: list[Project] = []

            for project in project_data.get(
                "projects",
                [],
            ):
                # Fetch latest deployment
                async with session.get(
                    f"{self.BASE_URL}/v6/deployments",
                    params={
                        "projectId": (project["id"]),
                        "limit": 1,
                        **params,
                    },
                ) as response:
                    response.raise_for_status()

                    deployment_data = await response.json()

                deployments = deployment_data.get(
                    "deployments",
                    [],
                )

                latest = deployments[0] if deployments else None

                projects.append(
                    Project(
                        id=project.get("id"),
                        name=project.get("name"),
                        framework=project.get("framework"),
                        production_domain=(
                            project.get(
                                "targets",
                                {},
                            )
                            .get(
                                "production",
                                {},
                            )
                            .get("alias")
                        ),
                        is_deployed=(latest is not None),
                        is_live=(
                            latest is not None and latest.get("readyState") == "READY"
                        ),
                    )    
                )
            await session.close()
            return projects
