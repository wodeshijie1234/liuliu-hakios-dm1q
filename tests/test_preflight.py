import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from preflight import public_properties, evaluate


class PublicInventoryTest(unittest.TestCase):
    def test_public_inventory_excludes_private_device_identifiers(self):
        output = public_properties({
            'ro.product.model': 'SM-S9110',
            'ro.product.device': 'dm1q',
            'ro.soc.model': 'SM8550',
            'ro.serialno': 'PRIVATE_SERIAL_SENTINEL',
            'ril.serialnumber': 'PRIVATE_RADIO_SENTINEL',
            'gsm.sim.operator.numeric': 'PRIVATE_SIM_SENTINEL',
            'persist.example': 'PRIVATE_OTHER_SENTINEL',
        })
        self.assertEqual(output, {
            'ro.product.model': 'SM-S9110',
            'ro.product.device': 'dm1q',
            'ro.soc.model': 'SM8550',
        })
        self.assertNotIn('PRIVATE_', json.dumps(output))


class PreparationGateTest(unittest.TestCase):
    def test_s23_plus_is_rejected_even_with_same_soc(self):
        result = evaluate({'properties': {
            'ro.product.model': 'SM-S9160',
            'ro.product.device': 'dm2q',
            'ro.soc.model': 'SM8550',
        }}, {})
        self.assertFalse(result['ready'])
        self.assertIn('DEVICE_MISMATCH', result['blockers'])

    def test_missing_recovery_files_block_exact_target(self):
        result = evaluate({'properties': {
            'ro.product.model': 'SM-S9110',
            'ro.product.device': 'dm1q',
            'ro.soc.model': 'SM8550',
        }}, {})
        self.assertFalse(result['ready'])
        self.assertIn('RECOVERY_INCOMPLETE', result['blockers'])

    def test_nonempty_recovery_claim_does_not_bypass_file_verification(self):
        result = evaluate({'properties': {
            'ro.product.model': 'SM-S9110',
            'ro.product.device': 'dm1q',
            'ro.soc.model': 'SM8550',
            'ro.boot.rp': '8',
        }}, {'model': 'SM-S9110', 'rollback_index': 8,
             'files': {'BL': {'path': '/missing/BL.tar', 'sha256': '0' * 64}}})
        self.assertFalse(result['ready'])
        self.assertIn('RECOVERY_INCOMPLETE', result['blockers'])


if __name__ == '__main__':
    unittest.main()
