# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.


class BookingDetails:
    def __init__(
        self,
        init_text: str = None,
        destination: str = None,
        origin: str = None,
        start_travel_date: str = None,
        return_travel_date: str = None,
        budget = None,
    ):
        self.init_text = init_text
        self.destination = destination
        self.origin = origin
        self.start_travel_date = start_travel_date
        self.return_travel_date = return_travel_date
        self.budget = budget
