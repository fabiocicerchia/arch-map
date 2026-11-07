@domain:documentation-site @area:theme-and-branding @from:stylesheets/extra
Feature: Branding the documentation site
  Gives readers of the arch-map docs and splash page one consistent, offline-safe look that identifies the project family.

  Background:
    Given the arch-map documentation site is built from the project's docs

  @id:docs.documentation-site.theme-and-branding.001 @rule:docs.theme.shared-accent-palette @inferred @source:docs/stylesheets/extra.css#:root @questionable
  Scenario: The docs and the splash page share the project's blue accent pair
    Given the project's accent pair is sky blue #38bdf8 and blue #3b82f6
    When a reader opens the rendered docs and the splash page
    Then the docs primary colour, links and primary buttons use the accent pair
    And the splash page uses the same accent pair
    And changing the pair in the one theme stylesheet changes both pages

  @id:docs.documentation-site.theme-and-branding.002 @rule:docs.theme.no-network-fonts @inferred @source:docs/stylesheets/extra.css#:root
  Scenario: The docs render with system fonts and download nothing
    Given the reader's machine has no access to font CDNs
    When a reader opens any docs page
    Then body text uses the system sans-serif stack starting with -apple-system and Segoe UI
    And code uses the system monospace stack starting with ui-monospace
    And no web font is requested

  @id:docs.documentation-site.theme-and-branding.003 @rule:docs.theme.links-legible-in-both-schemes @inferred @source:docs/stylesheets/extra.css#[data-md-color-scheme="slate"]
  Scenario Outline: Links stay readable in both the light and the dark scheme
    Given the docs offer a light scheme and a dark slate scheme
    When a reader views a page in the <scheme> scheme
    Then links are shown in <link_colour>
    And the page background is <background>

    Examples:
      | scheme     | link_colour      | background                 |
      | light      | blue #3b82f6     | the Material default white |
      | dark slate | sky blue #38bdf8 | near-black #0b0f1a         |

  @id:docs.documentation-site.theme-and-branding.004 @rule:docs.theme.no-borrowed-logo @inferred @source:docs/stylesheets/extra.css#.md-header__button.md-logo
  Scenario: The header shows no stand-in logo while the project has none
    Given no logo is configured for the docs site
    When a reader opens any docs page
    Then the header shows the site title without a logo icon
    And the navigation drawer title shows no logo icon

  @id:docs.documentation-site.theme-and-branding.005 @rule:docs.theme.wide-tables-visible-on-narrow-screens @inferred @source:docs/stylesheets/extra.css#.md-typeset table:not([class]) @questionable
  Scenario: Wide tables are clipped on narrow screens
    Given a docs page holds a table wider than the reader's screen
    When a reader views that page on a narrow screen
    Then the table is drawn as a rounded, bordered card with uppercase headers
    And the columns past the card's edge are cut off and cannot be scrolled into view
