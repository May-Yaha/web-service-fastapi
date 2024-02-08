"""
This module contains the process class.
"""

import time
import random
from fastapi import Request, HTTPException

from yaha.log.log import LogHelper
from yaha.web_api.factory import HandlerFactory


class RequestProcess:
    def __init__(self, request: Request, handler_type: str):
        self.request = request
        self.handler_type = handler_type

        self._set_log_id()

        self.app_handler, self.request_handler = HandlerFactory.get_handler(handler_type)
        self.request_model = HandlerFactory._context[handler_type].get("request")
        self.response_model = HandlerFactory._context[handler_type].get("response")

    def _set_log_id(self):
        """
        Sets the log id.
        :return:
        """
        log_id = self.request.headers.get("logid", str(int(time.time() * 1000)) + str(random.randint(0, 9999)))

        LogHelper.set_logid(log_id)
        LogHelper.info(f"Request handler type: {self.handler_type}")

    async def process_request(self):
        """
        Process the request.
        :return:
        """
        try:
            request_data = await self._parse_request_data()
            LogHelper.info(f"_parse_request_data: {request_data}")

            pre_processed = self.request_handler.pre_process(request_data)
            LogHelper.info(f"pre_process: {pre_processed}")

            result = self.request_handler.run(pre_processed)
            LogHelper.info(f"run: {result}")

            post_processed_result = self.request_handler.post_process(result)
            LogHelper.info(f"post_process: {post_processed_result}")

            return self._format_response(post_processed_result)
        except Exception as e:
            LogHelper.error(f"Failed to process request: {e}")
            raise HTTPException(status_code=400, detail=str(e)) from e

    async def _parse_request_data(self):
        """
        Parse the request data.
        :return:
        """
        LogHelper.info(f"headerType: {self.handler_type} Request body: {self.request}")
        if self.request_model:
            try:
                request_body = await self.request.json()
                return self.request_model(**request_body)
            except Exception as e:
                LogHelper.error(f"request Validation error: {e}")
                raise HTTPException(status_code=422, detail="Invalid request data") from e

        return await self.request.json()

    def _format_response(self, post_processed_result):
        """
        Format the response.
        :param post_processed_result:
        :return:
        """
        if self.response_model:
            try:
                return self.response_model(**post_processed_result)
            except Exception as e:
                LogHelper.error(f"response Validation error: {e}")
                raise HTTPException(status_code=422, detail="Invalid response data") from e

        return post_processed_result
