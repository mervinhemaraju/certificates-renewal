
resource "aws_scheduler_schedule_group" "certificates_renewal" {
  name = local.constants.scheduler.group_name
}

# resource "aws_scheduler_schedule" "helios_web_renewals" {

#   name                = "schedule-helios-web-renewal"
#   description         = "The schedule for renewing the SSL certificates for the Helios web Load Balancer."
#   group_name          = aws_scheduler_schedule_group.certificates_renewal.name
#   schedule_expression = "cron(0 9 ? * SUN#1 *)"
#   state               = "ENABLED"

#   schedule_expression_timezone = "Indian/Mauritius"

#   flexible_time_window {
#     mode = "OFF"
#   }

#   target {
#     arn      = module.lambda_renew_web_helios.lambda_function_arn
#     role_arn = module.iam_role_scheduler_renew_web_helios.iam_role_arn

#     retry_policy {
#       maximum_retry_attempts = 0
#     }
#   }

#   depends_on = [
#     aws_scheduler_schedule_group.certificates_renewal,
#     module.lambda_renew_web_helios,
#     module.iam_role_scheduler_renew_web_helios
#   ]
# }
