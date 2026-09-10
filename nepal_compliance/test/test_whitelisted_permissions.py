# Copyright (c) 2026, Yarsa Labs Pvt. Ltd. and Contributors
# See license.txt

import sys
import unittest
from unittest.mock import MagicMock, patch

# Ensure frappe and hrms modules are available for standalone test runners
if "frappe" not in sys.modules:
    frappe_mock = MagicMock()
    frappe_mock.whitelist = lambda *args, **kwargs: (lambda fn: fn)
    frappe_mock._ = lambda msg: msg
    frappe_mock.PermissionError = type("PermissionError", (Exception,), {})
    sys.modules["frappe"] = frappe_mock
    sys.modules["frappe.utils"] = MagicMock()
    sys.modules["frappe.utils.data"] = MagicMock()
    sys.modules["frappe.utils.password"] = MagicMock()
    sys.modules["frappe.utils.background_jobs"] = MagicMock()
    sys.modules["frappe.model"] = MagicMock()
    sys.modules["frappe.model.document"] = MagicMock()

if "hrms" not in sys.modules:
    hrms_mock = MagicMock()
    sys.modules["hrms"] = hrms_mock
    sys.modules["hrms.hr"] = MagicMock()
    sys.modules["hrms.hr.doctype"] = MagicMock()
    sys.modules["hrms.hr.doctype.leave_policy_assignment"] = MagicMock()
    sys.modules["hrms.hr.doctype.leave_policy_assignment.leave_policy_assignment"] = MagicMock()
    sys.modules["hrms.hr.doctype.leave_allocation"] = MagicMock()
    sys.modules["hrms.hr.doctype.leave_allocation.leave_allocation"] = MagicMock()

from nepal_compliance.cbms_api import sync_failed_cbms_invoices
from nepal_compliance.custom_code.leave_allocation.monthly_leave_bs import allocate_monthly_leave_bs
from nepal_compliance.setup.install import (
    check_test_data_status,
    generate_test_masters,
    generate_test_transactions,
)
from nepal_compliance.setup.uninstall import clear_test_data


class TestWhitelistedEndpointsPermissions(unittest.TestCase):
    """
    Tests for permission guards on whitelisted privileged endpoints (Issue #304).
    Verifies that unauthorized callers are rejected with frappe.PermissionError
    and authorized callers can proceed past the permission check.
    """

    @patch("nepal_compliance.cbms_api.frappe")
    def test_sync_failed_cbms_invoices_unauthorized(self, mock_frappe):
        mock_frappe.has_permission.return_value = False
        mock_frappe.PermissionError = type("PermissionError", (Exception,), {})
        mock_frappe.throw.side_effect = lambda msg, exc=Exception: (_ for _ in ()).throw(exc(msg))

        with self.assertRaises(mock_frappe.PermissionError):
            sync_failed_cbms_invoices()

        mock_frappe.has_permission.assert_called_with("CBMS Settings", "write")

    @patch("nepal_compliance.cbms_api.frappe")
    def test_sync_failed_cbms_invoices_authorized(self, mock_frappe):
        mock_frappe.has_permission.return_value = True
        mock_frappe.get_all.return_value = []

        res = sync_failed_cbms_invoices()
        self.assertEqual(res, {"message": 0})
        mock_frappe.has_permission.assert_called_with("CBMS Settings", "write")

    @patch("nepal_compliance.custom_code.leave_allocation.monthly_leave_bs.frappe")
    def test_allocate_monthly_leave_bs_unauthorized(self, mock_frappe):
        mock_frappe.has_permission.return_value = False
        mock_frappe.PermissionError = type("PermissionError", (Exception,), {})
        mock_frappe.throw.side_effect = lambda msg, exc=Exception: (_ for _ in ()).throw(exc(msg))

        with self.assertRaises(mock_frappe.PermissionError):
            allocate_monthly_leave_bs(bs_year=2081, bs_month=5, leave_types=["Casual Leave"])

        mock_frappe.has_permission.assert_called_with("Leave Allocation", "create")

    @patch("nepal_compliance.custom_code.leave_allocation.monthly_leave_bs.frappe")
    def test_allocate_monthly_leave_bs_authorized(self, mock_frappe):
        mock_frappe.has_permission.return_value = True
        mock_frappe.get_all.return_value = []
        mock_frappe.db.get_single_value.return_value = 0

        res = allocate_monthly_leave_bs(bs_year=2081, bs_month=5, leave_types=None)
        self.assertEqual(res["status"], "skipped")
        mock_frappe.has_permission.assert_called_with("Leave Allocation", "create")

    @patch("nepal_compliance.setup.install.frappe")
    def test_generate_test_masters_unauthorized(self, mock_frappe):
        mock_frappe.has_permission.return_value = False
        mock_frappe.PermissionError = type("PermissionError", (Exception,), {})
        mock_frappe.throw.side_effect = lambda msg, exc=Exception: (_ for _ in ()).throw(exc(msg))

        with self.assertRaises(mock_frappe.PermissionError):
            generate_test_masters("IRD-001")

        mock_frappe.has_permission.assert_called_with("IRD Certification", "write")

    @patch("nepal_compliance.setup.install.frappe")
    def test_generate_test_transactions_unauthorized(self, mock_frappe):
        mock_frappe.has_permission.return_value = False
        mock_frappe.PermissionError = type("PermissionError", (Exception,), {})
        mock_frappe.throw.side_effect = lambda msg, exc=Exception: (_ for _ in ()).throw(exc(msg))

        with self.assertRaises(mock_frappe.PermissionError):
            generate_test_transactions("IRD-001")

        mock_frappe.has_permission.assert_called_with("IRD Certification", "write")

    @patch("nepal_compliance.setup.install.frappe")
    def test_check_test_data_status_unauthorized(self, mock_frappe):
        mock_frappe.has_permission.return_value = False
        mock_frappe.PermissionError = type("PermissionError", (Exception,), {})
        mock_frappe.throw.side_effect = lambda msg, exc=Exception: (_ for _ in ()).throw(exc(msg))

        with self.assertRaises(mock_frappe.PermissionError):
            check_test_data_status("IRD-001")

        mock_frappe.has_permission.assert_called_with("IRD Certification", "read")

    @patch("nepal_compliance.setup.uninstall.frappe")
    def test_clear_test_data_unauthorized(self, mock_frappe):
        mock_frappe.has_permission.return_value = False
        mock_frappe.PermissionError = type("PermissionError", (Exception,), {})
        mock_frappe.throw.side_effect = lambda msg, exc=Exception: (_ for _ in ()).throw(exc(msg))

        with self.assertRaises(mock_frappe.PermissionError):
            clear_test_data("IRD-001")

        mock_frappe.has_permission.assert_called_with("IRD Certification", "write")


if __name__ == "__main__":
    unittest.main()
