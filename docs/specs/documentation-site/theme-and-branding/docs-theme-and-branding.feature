@domain:documentation-site @area:theme-and-branding @from:stylesheets/extra
Feature: Branding the documentation site
  Gives readers of the arch-map docs and splash page one consistent, offline-safe look that identifies the project family.

  Background:
    Given the arch-map documentation site is built from the project's docs

  @id:docs.documentation-site.theme-and-branding.002 @rule:docs.theme.no-network-fonts @inferred @source:docs/stylesheets/extra.css#:root
  Scenario: The docs render with system fonts and download nothing
    Given the reader's machine has no access to font CDNs
    When a reader opens any docs page
    Then body text uses the system sans-serif stack starting with -apple-system and Segoe UI
    And code uses the system monospace stack starting with ui-monospace
    And no web font is requested

  @id:docs.documentation-site.theme-and-branding.005 @rule:docs.theme.wide-tables-visible-on-narrow-screens @inferred @source:docs/stylesheets/extra.css#.md-typeset table:not([class]) @questionable
  Scenario: Wide tables are clipped on narrow screens
    Given a docs page holds a table wider than the reader's screen
    When a reader views that page on a narrow screen
    Then the table is drawn as a rounded, bordered card with uppercase headers
    And the columns past the card's edge are cut off and cannot be scrolled into view
