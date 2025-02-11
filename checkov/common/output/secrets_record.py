from __future__ import annotations

import logging
import os
from typing import Optional, List, Tuple, Dict, Any

from termcolor import colored

from checkov.common.models.enums import CheckResult
from checkov.secrets.consts import ValidationStatus

from checkov.common.bridgecrew.severities import Severity

from checkov.common.output.record import Record
from checkov.common.typing import _CheckResult

WARNING_SIGN_UNICODE = '\u26a0'
TEXT_BY_SECRET_VALIDATION_STATUS = {
    ValidationStatus.VALID.value: colored(f'\t{WARNING_SIGN_UNICODE} This secret has been validated'
                                          f' and should be prioritized', "red"),
    ValidationStatus.INVALID.value: '\tThis is not a valid secret and can be de-prioritized',
    ValidationStatus.UNKNOWN.value: '\tWe were not able to validate this secret',
    ValidationStatus.UNAVAILABLE.value: ''
}


class SecretsRecord(Record):
    def __init__(self,
                 check_id: str,
                 check_name: str,
                 check_result: _CheckResult,
                 code_block: List[Tuple[int, str]],
                 file_path: str,
                 file_line_range: List[int],
                 resource: str,
                 evaluations: Optional[Dict[str, Any]],
                 check_class: str,
                 file_abs_path: str,
                 entity_tags: Optional[Dict[str, str]] = None,
                 caller_file_path: Optional[str] = None,
                 caller_file_line_range: Optional[Tuple[int, int]] = None,
                 bc_check_id: Optional[str] = None,
                 resource_address: Optional[str] = None,
                 severity: Optional[Severity] = None,
                 bc_category: Optional[str] = None,
                 benchmarks: dict[str, list[str]] | None = None,
                 description: Optional[str] = None,
                 short_description: Optional[str] = None,
                 vulnerability_details: Optional[Dict[str, Any]] = None,
                 connected_node: Optional[Dict[str, Any]] = None,
                 details: Optional[List[str]] = None,
                 check_len: int | None = None,
                 definition_context_file_path: Optional[str] = None,
                 validation_status: Optional[str] = None,
                 added_commit_hash: Optional[str] = None,
                 removed_commit_hash: Optional[str] = None
                 ):
        super().__init__(check_id=check_id,
                         check_name=check_name,
                         check_result=check_result,
                         code_block=code_block,
                         file_path=file_path,
                         file_line_range=file_line_range,
                         resource=resource,
                         evaluations=evaluations,
                         check_class=check_class,
                         file_abs_path=file_abs_path,
                         entity_tags=entity_tags,
                         bc_check_id=bc_check_id,
                         severity=severity,
                         details=details,
                         caller_file_path=caller_file_path,
                         caller_file_line_range=caller_file_line_range,
                         resource_address=resource_address,
                         bc_category=bc_category,
                         benchmarks=benchmarks,
                         description=description,
                         short_description=short_description,
                         vulnerability_details=vulnerability_details,
                         connected_node=connected_node,
                         check_len=check_len,
                         definition_context_file_path=definition_context_file_path
                         )
        self.validation_status = validation_status
        self.added_commit_hash = added_commit_hash
        self.removed_commit_hash = removed_commit_hash

    def to_string(self, compact: bool = False, use_bc_ids: bool = False) -> str:
        processed_record = super().to_string(compact=compact, use_bc_ids=use_bc_ids)
        validation_status_message = self._get_secret_validation_status_message()
        if validation_status_message and self.check_result["result"] == CheckResult.FAILED and os.getenv("CKV_VALIDATE_SECRETS"):
            # if needed insert validation status message
            splitted_record = processed_record.split("\n")
            splitted_record.insert(2, validation_status_message)
            processed_record = "\n".join(splitted_record)
        return processed_record

    def _get_secret_validation_status_message(self) -> str:
        message = None
        if self.validation_status:
            message = TEXT_BY_SECRET_VALIDATION_STATUS.get(self.validation_status)

            if not message and self.validation_status != ValidationStatus.UNAVAILABLE.value:
                logging.debug(f'Got empty message for secret validation status = {self.validation_status}')

        return message or ''
