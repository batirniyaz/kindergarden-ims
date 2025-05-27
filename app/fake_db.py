import asyncio
import httpx
import random
from faker import Faker
from datetime import datetime
import json
import os
from typing import List, Dict, Optional, Any


class FakeDataGenerator:
    def __init__(self, base_url: str = "http://10.30.0.101:1111", admin_username: str = "admin",
                 admin_password: str = "admin"):
        self.faker = Faker()
        self.base_url = base_url
        self.admin_credentials = {"username": admin_username, "password": admin_password}
        self.users = []
        self.roles = ["admin", "manager", "cook"]
        self.admin_token = None

    async def get_admin_token(self) -> str:
        """Login as admin and return token"""
        if self.admin_token:
            return self.admin_token

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/auth/login",
                data=self.admin_credentials
            )

            if response.status_code != 200:
                raise Exception(f"Admin login failed: {response.text}")

            self.admin_token = response.json()["access_token"]
            return self.admin_token

    async def create_users(self, count: int = 10) -> List[Dict[str, Any]]:
        """Create fake users and store them in the instance"""
        admin_token = await self.get_admin_token()
        headers = {"Authorization": f"Bearer {admin_token}"}

        async with httpx.AsyncClient() as client:
            for i in range(count):
                user_data = {
                    "username": self.faker.user_name() + str(i),
                    "password": "123",
                    "email": self.faker.email(),
                    "phone": "+998" + random.choice(["90", "91", "93", "94", "88", "50", "51"]) +
                             "".join([str(random.randint(0, 9)) for _ in range(7)]),
                    "first_name": self.faker.first_name(),
                    "last_name": self.faker.last_name(),
                    "role": random.choice(self.roles)
                }

                response = await client.post(
                    f"{self.base_url}/user/",
                    json=user_data,
                    headers=headers
                )

                if response.status_code == 200:
                    self.users.append(user_data)
                    print(f"Created user: {user_data['username']}")
                else:
                    print(f"Failed to create user: {response.text}")

        return self.users

    async def login_user(self, username: Optional[str] = None) -> Dict[str, Any]:
        """Login as specific user or random user and return token"""
        if not self.users and not username:
            raise Exception("No users available. Create users first.")

        user = None
        if username:
            user = next((u for u in self.users if u["username"] == username), None)
        else:
            user = random.choice(self.users)

        if not user:
            raise Exception(f"User {username} not found")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/auth/login",
                data={"username": user["username"], "password": "123"}
            )

            if response.status_code != 200:
                raise Exception(f"Login failed for {user['username']}: {response.text}")

            token = response.json()["access_token"]
            return {
                "user": user,
                "token": token,
                "headers": {"Authorization": f"Bearer {token}"}
            }

    async def simulate_logins(self, count: int = 50) -> None:
        """Simulate multiple user logins and profile accesses"""
        if not self.users:
            raise Exception("No users available. Create users first.")

        async with httpx.AsyncClient() as client:
            for _ in range(count):
                user = random.choice(self.users)

                login_resp = await client.post(
                    f"{self.base_url}/auth/login",
                    data={"username": user["username"], "password": "123"}
                )

                if login_resp.status_code == 200:
                    token = login_resp.json()["access_token"]
                    headers = {"Authorization": f"Bearer {token}"}

                    # Access profile
                    await client.get(f"{self.base_url}/auth/me/", headers=headers)

                    # Logout (sometimes)
                    if random.random() > 0.3:
                        await client.post(f"{self.base_url}/auth/logout", headers=headers)
                        print(f"User {user['username']} logged out")
                    else:
                        print(f"User {user['username']} stayed logged in")
                else:
                    print(f"Login failed for {user['username']}. Response: {login_resp.text}")

    async def create_ingredient(self, name: Optional[str] = None, user_role: str = "manager") -> Dict[str, Any]:
        """Create an ingredient using a user with specific role"""
        eligible_users = [u for u in self.users if u["role"] == user_role]

        if not eligible_users:
            raise Exception(f"No users with role {user_role} available")

        user_data = await self.login_user(random.choice(eligible_users)["username"])

        ingredient_name = name or f"{self.faker.word()}"
        ingredient_data = {
            "name": ingredient_name,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/ingredient/",  # Adjust endpoint as needed
                json=ingredient_data,
                headers=user_data["headers"]
            )

            if response.status_code == 200:
                print(f"Created ingredient: {ingredient_name}")
                return response.json()
            else:
                print(f"Failed to create ingredient: {response.text}")
                return {}

    async def get_users(self, limit: Optional[int] = 10, page: Optional[int] = 1, role: Optional[str] = None) -> List[Dict[str, Any]] or None:
        """Get all users or filter by role"""
        admin_token = await self.get_admin_token()
        headers = {"Authorization": f"Bearer {admin_token}"}

        async with httpx.AsyncClient() as client:
            url = f"{self.base_url}/user/"
            if limit and page:
                url += f"?limit={limit}&page={page}"
            if role:
                url += f"&role={role}"
            response = await client.get(url, headers=headers)

            if response.status_code == 200:
                users_data = response.json()
                self.users = users_data
                return users_data
            else:
                print(f"Failed to fetch users: {response.text}")
                return self.users


    async def get_ingredients(self, limit: Optional[int] = 10, page: Optional[int] = 1) -> List[Dict[str, Any]] or None:
        """Get all ingredients"""
        admin_token = await self.get_admin_token()
        headers = {"Authorization": f"Bearer {admin_token}"}

        async with httpx.AsyncClient() as client:
            url = f"{self.base_url}/ingredient/"
            if limit and page:
                url += f"?limit={limit}&page={page}"
            response = await client.get(url, headers=headers)

            if response.status_code == 200:
                ingredients_data = response.json()
                return ingredients_data
            else:
                print(f"Failed to fetch ingredients: {response.text}")
                return []

    async def create_delivery(self, user_role: str = "manager") -> Dict[str, Any]:
        """Create a delivery for an ingredient using a user with specific role"""
        eligible_users = [u for u in self.users if u["role"] == user_role]
        ingredients = await self.get_ingredients(limit=15, page=1)

        ing_ids = [ing["id"] for ing in ingredients['items']]
        rand_ings = random.sample(ing_ids, 6)

        if not eligible_users:
            raise Exception(f"No users with role {user_role} available")

        created_delivery = {}
        for ing in rand_ings:
            user_data = await self.login_user(random.choice(eligible_users)["username"])

            delivery_data = {
                "ingredient_id": ing,
                "weight": random.uniform(1000.0, 10000.0)
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/delivery/",  # Adjust endpoint as needed
                    json=delivery_data,
                    headers=user_data["headers"]
                )

            if response.status_code == 200:
                print(f"Created delivery for ingredient ID {ing}")
                created_delivery[ing] = response.json()
            else:
                print(f"Failed to create delivery: {response.text}")

        return created_delivery

    async def create_meal(self, user_role: str = "manager") -> Dict[str, Any]:
        """Create a meal using a user with specific role"""
        eligible_users = [u for u in self.users if u["role"] == user_role]

        if not eligible_users:
            raise Exception(f"No users with role {user_role} available")

        user_data = await self.login_user(random.choice(eligible_users)["username"])

        meal_data = {
            "name": f"{self.faker.word()}"}

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/meal/",  # Adjust endpoint as needed
                json=meal_data,
                headers=user_data["headers"]
            )

        if response.status_code == 200:
            print(f"Created meal: {meal_data['name']}")
            return response.json()
        else:
            print(f"Failed to create meal: {response.text}")
            return {}


async def main():
    # Example usage
    generator = FakeDataGenerator()

    await generator.get_users(role="manager")


    # ingredients = await generator.get_ingredients(limit=15, page=1)
    # deliveries = await generator.create_delivery()
    # print(json.dumps(deliveries, indent=4))
    # print(f"Fetched {len(users)} users and {len(ingredients)} ingredients.")
    # print("Ingredients:", json.dumps(ingredients, indent=2))
    # print("Users:", json.dumps(users, indent=2))

    for _ in range(5):
        await generator.create_meal()

    # await generator.create_users(10)
    #
    # # Simulate some logins
    # await generator.simulate_logins(5)
    #
    # # Create ingredients with admin user
    # for _ in range(10):
    #     await generator.create_ingredient()


if __name__ == "__main__":
    asyncio.run(main())