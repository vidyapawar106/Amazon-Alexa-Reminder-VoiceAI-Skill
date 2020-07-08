# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import logging
import ask_sdk_core.utils as ask_utils
import typing

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response

from datetime import datetime
from ask_sdk_core.skill_builder import CustomSkillBuilder
from ask_sdk_model.ui import SimpleCard
from ask_sdk_core.api_client import DefaultApiClient
from ask_sdk_model.services.reminder_management import (
    ReminderRequest, Trigger, TriggerType, AlertInfo, PushNotification,
    PushNotificationStatus, ReminderResponse, SpokenInfo, SpokenText)
from ask_sdk_model.services import ServiceException
from ask_sdk_model.ui import AskForPermissionsConsentCard

permissions = ["alexa::alerts:reminders:skill:readwrite"]
NOTIFY_MISSING_PERMISSIONS = ("Please enable Reminders permissions in "
                              "the Amazon Alexa app.")

class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Welcome to RemindME. Would you like to schedule a reminder?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class CreateReminderIntentHandler(AbstractRequestHandler):
    
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_request_type("IntentRequest")(handler_input) and
                ask_utils.is_intent_name("AMAZON.YesIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        reminder_client = handler_input.service_client_factory.get_reminder_management_service()
        req_envelope = handler_input.request_envelope
        response_builder = handler_input.response_builder
        
    # Check if user gave permissions to create reminders.
    # If not, request to provide permissions to the skill.
        if not (req_envelope.context.system.user.permissions and
                req_envelope.context.system.user.permissions.consent_token):
            response_builder.speak(NOTIFY_MISSING_PERMISSIONS)
            response_builder.set_card(
            AskForPermissionsConsentCard(permissions=permissions))
            return response_builder.response
        
        try:
            reminder_response = reminder_client.create_reminder(
            reminder_request=ReminderRequest(
                request_time=datetime.utcnow(),
                trigger=Trigger(
                    object_type=TriggerType.SCHEDULED_RELATIVE,
                    offset_in_seconds=60),
                alert_info=AlertInfo(
                    spoken_info=SpokenInfo(
                        content=[SpokenText(locale="en-US", text="Test reminder")])),
                push_notification=PushNotification(
                    status=PushNotificationStatus.ENABLED))) # type: ReminderResponse
            speech_text = "Great! I've scheduled a reminder for you."

            logger.info("Created reminder : {}".format(reminder_response))
            return handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard(
                "Reminder created with id", reminder_response.alert_token)).response

        except ServiceException as e:
            logger.info("Exception encountered : {}".format(e.body))
            speech_text = "Uh Oh. Looks like something went wrong."
            return handler_input.response_builder.speak(speech_text).set_card(
                SimpleCard(
                    "Reminder not created",str(e.body))).response
            
        speak_output = "Your reminder has been scheduled successfully."
        return (
            handler_input.response_builder
                .speak(speak_text)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
            )

    
class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "You can say hello to me! How can I help?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Goodbye!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.


sb = CustomSkillBuilder(api_client=DefaultApiClient())

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(CreateReminderIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())


lambda_handler = sb.lambda_handler()


