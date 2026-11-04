"""Exercise the boundaries that prevent a misleading readiness result."""
import asyncio
import unittest

from aiohttp.test_utils import AioHTTPTestCase

from app.server import CHECKS, make_app


class ReadinessTests(AioHTTPTestCase):
    async def get_application(self):
        return make_app(":memory:")

    async def new_flight(self):
        response = await self.client.post("/api/session", json={})
        self.assertEqual(response.status, 200)
        state = await response.json()
        return {"X-Flight-Session": state["session"]}, state

    async def answer(self, headers, check, value="yes"):
        response = await self.client.post("/api/confirm", headers=headers, json={"check": check, "value": value})
        self.assertEqual(response.status, 200)
        return await response.json()

    async def echo(self, state):
        ws = await self.client.ws_connect("/ws")
        await ws.send_json({"session": state["session"]})
        first = await ws.receive_json()
        self.assertFalse(first["connection"])
        await ws.send_json({"echo": first["nonce"]})
        second = await ws.receive_json()
        self.assertTrue(second["connection"])
        return ws, second

    async def test_visual_confirmations_alone_do_not_pass_a_blocked_socket(self):
        headers, _ = await self.new_flight()
        for key in CHECKS:
            state = await self.answer(headers, key)
        self.assertIsNone(state["completed_at"])
        self.assertEqual((await self.client.get("/api/completion")).status, 409)

    async def test_socket_alone_does_not_pass_and_four_confirmations_complete(self):
        headers, state = await self.new_flight()
        ws, echoed = await self.echo(state)
        try:
            self.assertIsNone(echoed["completed_at"])
            self.assertEqual((await self.client.get("/api/completion")).status, 409)
            for key in CHECKS:
                result = await self.answer(headers, key)
            self.assertIsNotNone(result["completed_at"])
            self.assertEqual((await self.client.get("/api/completion")).status, 200)
            # A guest who notices a problem can correct a previously successful check.
            corrected = await self.answer(headers, "editor", "issue")
            self.assertIsNone(corrected["completed_at"])
            self.assertEqual((await self.client.get("/api/completion")).status, 409)
        finally:
            await ws.close()

    async def test_upgrade_without_round_trip_does_not_pass(self):
        headers, state = await self.new_flight()
        ws = await self.client.ws_connect("/ws")
        await ws.send_json({"session": state["session"]})
        await ws.receive_json()
        await ws.send_json({"echo": "wrong nonce"})
        self.assertFalse((await ws.receive_json())["connection"])
        for key in CHECKS:
            result = await self.answer(headers, key)
        self.assertIsNone(result["completed_at"])
        await ws.close()

    async def test_independent_browsers_cannot_read_or_change_each_others_answers(self):
        first_headers, first = await self.new_flight()
        second_headers, second = await self.new_flight()
        self.assertNotEqual(first["session"], second["session"])
        await self.answer(first_headers, "ziggy")
        response = await self.client.post("/api/session", headers=second_headers, json={})
        self.assertEqual((await response.json())["checks"]["ziggy"], "unset")
        unknown = {"X-Flight-Session": "invented-session"}
        response = await self.client.post("/api/confirm", headers=unknown, json={"check": "ziggy", "value": "yes"})
        self.assertEqual(response.status, 404)
        response = await self.client.get("/api/report", headers=unknown)
        self.assertEqual(response.status, 404)

    async def test_concurrent_answers_do_not_lose_a_confirmation(self):
        headers, _ = await self.new_flight()
        await asyncio.gather(*(self.answer(headers, key) for key in CHECKS))
        response = await self.client.post("/api/session", headers=headers, json={})
        self.assertTrue(all(value == "yes" for value in (await response.json())["checks"].values()))

    async def test_malformed_answers_are_rejected(self):
        headers, _ = await self.new_flight()
        for payload in ([], {"check": []}, {"check": "editor", "value": []}, {"check": "fake", "value": "yes"}):
            response = await self.client.post("/api/confirm", headers=headers, json=payload)
            self.assertEqual(response.status, 400)

    async def test_incomplete_report_is_available_and_honest(self):
        headers, state = await self.new_flight()
        await self.answer(headers, "terminal", "issue")
        response = await self.client.get("/api/report", headers=headers)
        report = await response.text()
        self.assertIn("NEEDS ATTENTION / INCOMPLETE", report)
        self.assertIn("Live terminal output: issue", report)
        self.assertIn("Typing, editing, clipboard access", report)
        self.assertNotIn(state["session"], report)


if __name__ == "__main__":
    unittest.main()
