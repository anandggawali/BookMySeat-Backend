from repositories.config_repository import ConfigurationRepository


class ConfigurationService:

    @staticmethod
    def get_configuration():

        version = ConfigurationRepository.get_version_config()

        support = ConfigurationRepository.get_support_config()

        booking_rules = ConfigurationRepository.get_booking_rules()

        reject_reasons = ConfigurationRepository.get_reject_reasons()

        return {
            "status": 200,
            "message": "Configuration loaded successfully",
            "errorMessage": "",
            "data": {
                "config": {
                    "version": version,
                    "support": support
                },
                "masters": {
                    "rejectReason": reject_reasons,
                    "bookingRules": booking_rules
                }
            }
        }