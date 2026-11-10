@domain:terraform-discovery @area:state-loading @from:arch-map/arch-map
Feature: Rejecting unusable Terraform state
  Operators feeding arch-map a state file pulled from a backend or CI artifact get one clear line and a distinct exit code when that file cannot be used, instead of a traceback or an empty diagram.

  Background:
    Given the operator runs arch-map with a Terraform state file

  @id:terraform-discovery.state-loading.001 @rule:terraform.state-loading.unusable-file-reported-with-exit-code @verified @source:arch_map.py#read_tfstate @test:tests/test_arch_map.py#test_unusable_tfstate_is_one_line_and_an_exit_code @test:tests/test_arch_map.py#test_missing_tfstate_is_noinput
  Scenario Outline: An unusable state file is reported in one line with an exit code naming the problem
    Given the state file at "infra.tfstate" is <condition>
    When the operator generates the diagram from "infra.tfstate"
    Then arch-map exits with code <exit code>
    And stderr is a single line starting with "arch-map: infra.tfstate: " and containing "<message>"
    And no diagram is written

    Examples:
      | condition                        | exit code | message                                 |
      | missing                          | 66        | no such file                            |
      | empty                            | 65        | not valid terraform state               |
      | plain text, not JSON             | 65        | not valid terraform state               |
      | truncated mid-object             | 65        | not valid terraform state               |
      | not UTF-8                        | 65        | not valid UTF-8, so not terraform state |
      | 10,000 levels of nested brackets | 65        | nested too deeply to parse              |
      | valid JSON but not state         | 65        | valid JSON, but not terraform state     |
      | a directory or unreadable        | 74        | the operating system's reason           |
