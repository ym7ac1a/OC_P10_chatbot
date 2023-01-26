# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Flight booking dialog."""

from botbuilder.dialogs import WaterfallDialog, WaterfallStepContext, DialogTurnResult
from botbuilder.dialogs.prompts import ConfirmPrompt, TextPrompt, \
    PromptOptions, NumberPrompt
from botbuilder.schema import InputHints
from botbuilder.core import MessageFactory, BotTelemetryClient, \
    NullTelemetryClient
from botbuilder.core.bot_telemetry_client import Severity

from .cancel_and_help_dialog import CancelAndHelpDialog
from .date_resolver_dialog import DateResolverDialog
from datatypes_date_time.timex import Timex

class BookingDialog(CancelAndHelpDialog):
    """Flight booking implementation."""

    def __init__(
        self,
        dialog_id: str = None,
        telemetry_client: BotTelemetryClient = NullTelemetryClient(),
    ):
        super(BookingDialog, self).__init__(
            dialog_id or BookingDialog.__name__, telemetry_client
        )
        self.telemetry_client = telemetry_client
        text_prompt = TextPrompt(TextPrompt.__name__)
        text_prompt.telemetry_client = telemetry_client

        waterfall_dialog = WaterfallDialog(
            WaterfallDialog.__name__,
            [
                self.destination_step,
                self.origin_step,
                self.start_travel_date_step,
                self.return_travel_date_step,
                self.budget_step,
                self.confirm_step,
                self.final_step,
            ],
        )
        waterfall_dialog.telemetry_client = telemetry_client

        self.add_dialog(text_prompt)
        self.add_dialog(NumberPrompt(NumberPrompt.__name__))
        self.add_dialog(ConfirmPrompt(ConfirmPrompt.__name__))
        self.add_dialog(waterfall_dialog)

        self.add_dialog(
            DateResolverDialog(
                DateResolverDialog.START_DATE_DIALOG_ID, self.telemetry_client
            )
        )
        self.add_dialog(
            DateResolverDialog(
                DateResolverDialog.END_DATE_DIALOG_ID, self.telemetry_client
            )
        )

        self.initial_dialog_id = WaterfallDialog.__name__

    async def destination_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """Prompt for destination."""
        booking_details = step_context.options
        if booking_details.dst_city is None:
            return await step_context.prompt(
                TextPrompt.__name__,
                PromptOptions(
                    prompt=MessageFactory.text("Which city would you like to travel to?")
                ),
            )  # pylint: disable=line-too-long,bad-continuation

        return await step_context.next(booking_details.dst_city)

    async def origin_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """Prompt for origin city."""
        booking_details = step_context.options

        # Capture the response to the previous step's prompt
        booking_details.dst_city = step_context.result.capitalize()
        if booking_details.or_city is None:
            return await step_context.prompt(
                TextPrompt.__name__,
                PromptOptions(
                    prompt=MessageFactory.text("Which city will you travel from?")
                ),
            )  # pylint: disable=line-too-long,bad-continuation

        return await step_context.next(booking_details.or_city)

    async def start_travel_date_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """Prompt for starting travel date."""
        booking_details = step_context.options

        # Capture the results of the previous step
        booking_details.or_city = step_context.result

        if not booking_details.str_date or self.is_ambiguous(booking_details.str_date):
            return await step_context.begin_dialog(
                DateResolverDialog.START_DATE_DIALOG_ID,
                booking_details.str_date,
            )
        
        return await step_context.next(booking_details.str_date)

    async def return_travel_date_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """Prompt for starting travel date."""

        booking_details = step_context.options

        # Capture the results of the previous step
        booking_details.str_date = step_context.result

        if not booking_details.end_date or self.is_ambiguous(booking_details.end_date):
            return await step_context.begin_dialog(
                DateResolverDialog.END_DATE_DIALOG_ID, booking_details.end_date
            )

        return await step_context.next(booking_details.end_date)

    async def budget_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """Prompt for trip budget."""
        booking_details = step_context.options
        
        # Capture the response to the previous step's prompt
        booking_details.end_date = step_context.result

        if booking_details.budget is None:
            return await step_context.prompt(
                TextPrompt.__name__,
                PromptOptions(
                    prompt=MessageFactory.text(
                        "💸 How much money can you afford ($) ?"
                    )
                )                    
            )  # pylint: disable=line-too-long,bad-continuation

        return await step_context.next(booking_details.budget)

    async def confirm_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """Confirm the information the user has provided."""
        booking_details = step_context.options

        # Capture the results of the previous step
        booking_details.budget = step_context.result
        msg = f"""
Please confirm your trip details :
- 🛫 from : **{ booking_details.or_city }**
- 🛬 to : **{ booking_details.dst_city }**
- 🥳 departure date : **{ booking_details.str_date }**
- 😮‍💨 return date : **{ booking_details.end_date }**
- 💸 for a budget of : **{ booking_details.budget }** $
"""

        # Offer a YES/NO prompt.
        return await step_context.prompt(
            ConfirmPrompt.__name__,
            PromptOptions(prompt=MessageFactory.text(msg))
        )

    async def final_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """Complete the interaction, send data to Azure app insights and end the dialog."""
        
        # Data to be tracked in app insights
        booking_details = step_context.options
        
        # If positive answer
        if step_context.result:
            self.telemetry_client.track_trace(
                "BOOKING ACCEPTED",
                properties=booking_details.__dict__,
                severity="INFO"
            )
            return await step_context.end_dialog(booking_details)
        
        else:
            sorry_msg = "I'm sorry, hope to see you soon!"
            prompt_sorry_msg = MessageFactory.text(
                sorry_msg, sorry_msg, InputHints.ignoring_input)
            await step_context.context.send_activity(prompt_sorry_msg)
            
            self.telemetry_client.track_trace(
                "BOOKING REFUSED",
                properties=booking_details.__dict__,
                severity="ERROR"
            )
        return await step_context.end_dialog()
    
    def is_ambiguous(self, timex: str) -> bool:
        """Ensure time is correct."""
        timex_property = Timex(timex)
        return "definite" not in timex_property.types