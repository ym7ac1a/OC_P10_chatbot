# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Handle cancel and help intents."""

from botbuilder.core import BotTelemetryClient, NullTelemetryClient
from botbuilder.core.bot_telemetry_client import Severity
from botbuilder.dialogs import (
    ComponentDialog,
    DialogContext,
    DialogTurnResult,
    DialogTurnStatus,
)
from botbuilder.schema import ActivityTypes


class CancelAndHelpDialog(ComponentDialog):
    """Implementation of handling cancel and help."""

    def __init__(
        self,
        dialog_id: str,
        telemetry_client: BotTelemetryClient = NullTelemetryClient(),
    ):
        super(CancelAndHelpDialog, self).__init__(dialog_id)
        self.telemetry_client = telemetry_client

    async def on_begin_dialog(
        self, inner_dc: DialogContext, options: object
    ) -> DialogTurnResult:
        result = await self.interrupt(inner_dc)
        if result is not None:
            return result

        return await super(CancelAndHelpDialog, self).on_begin_dialog(inner_dc, options)

    async def on_continue_dialog(self, inner_dc: DialogContext) -> DialogTurnResult:
        result = await self.interrupt(inner_dc)
        if result is not None:
            return result

        return await super(CancelAndHelpDialog, self).on_continue_dialog(inner_dc)

    async def interrupt(self, inner_dc: DialogContext) -> DialogTurnResult:
        """Detect interruptions."""
        if inner_dc.context.activity.type == ActivityTypes.message:
            text = inner_dc.context.activity.text.lower()

            if text in ("help", "?"):
                self.telemetry_client.track_trace(
                    "ASKED FOR HELP",
                    severity="WARNING"
                )
                await inner_dc.context.send_activity(
                    """
Just tell me
- 🏙️ **Where** you want to travel to (cities of origin and destination).
Ex. : _'I want to travel from Seattle to San Francisco'_
- 📅 **When** you want to travel (dates of departure and return).
Ex. : _'I want to travel on May 1, 2020 and return on May 5, 2020'_
- 💸 **How much** is your budget for this trip.
Ex. : _'I want to travel for $500'_

Send **Cancel** to start over"""
                )
                return DialogTurnResult(DialogTurnStatus.Waiting)

            if text in ("cancel", "quit"):
                self.telemetry_client.track_trace(
                    "BOOKING CANCELLED",
                    severity="WARNING"   # Severity.WARNING.name
                )
                await inner_dc.context.send_activity(
                    "It's OK to change your mind 🧘")
                return await inner_dc.cancel_all_dialogs()

        return None
