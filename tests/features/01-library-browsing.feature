Feature: Browse the award library
  As a science-fiction reader
  I want to browse and filter the winners and finalists of seven awards
  So that I can find books worth reading

  Numbers come from tests/fixtures/facts.json (1,329 books, 296 with at least one win).

  Background:
    Given a fresh browser profile
    And the app is open on the Library tab

  # ---------- first load ----------

  @LIB-01 @smoke
  Scenario: The library loads with every book and sensible defaults
    Then the result count reads "1329 books match"
    And the "Show" filter is "Winners & finalists"
    And the "Status" filter is "All books"
    And the "Source" filter is "All books"
    And the "Decade" filter is "All years"
    And the "Group by" filter is "No grouping"
    And the "Sort" filter is "Most honoured"
    And no award filter is selected
    And the header counter reads "Read 0 / 1329"
    And no "Now reading" row is shown

  @LIB-02 @smoke
  Scenario: The first books are the most honoured ones
    Then the first card is "Ancillary Justice"
    And the second card is "Rendezvous with Rama"

  @LIB-03
  Scenario: Only the first page of cards is rendered and more can be loaded
    Then 60 cards are shown
    And a "Show more (60 of 1329)" button is shown
    When I tap "Show more"
    Then 120 cards are shown
    And the "Show more" button reads "Show more (120 of 1329)"

  @LIB-04 @smoke
  Scenario: A card shows the title, author, award badges and links
    Then the card for "Ancillary Justice" shows the author "Ann Leckie"
    And it shows the badges "★ Nebula 2013", "★ BSFA 2013", "★ Hugo 2014" and "★ Clarke 2014"
    And it shows the non-winning badges "Campbell 2014" and "PKD 2014" in a dimmer style
    And it has "Wikipedia" and "Goodreads" links for the book and "Wikipedia" and "ISFDB" links for the author
    And all of those links open in a new tab

  @LIB-05
  Scenario Outline: Outside links search for the right thing
    When I look at the "<link>" link of the card for "Dune"
    Then its address contains "<site>" and the text "<needle>"

    Examples:
      | link                | site          | needle |
      | Book Wikipedia      | wikipedia.org | Dune   |
      | Book Goodreads      | goodreads.com | Dune   |
      | Author Wikipedia    | wikipedia.org | Frank  |
      | Author ISFDB        | isfdb.org     | Frank  |

  # ---------- search ----------

  @LIB-10 @smoke
  Scenario: Search by title
    When I type "dune" in the search box
    Then the result count reads "3 books match"
    And the cards are "Children of Dune", "Dune" and "Dune World" in some order

  @LIB-11
  Scenario: Search by author
    When I type "leckie" in the search box
    Then the result count reads "5 books match"
    And every card has the author "Ann Leckie"

  @LIB-12
  Scenario Outline: Search ignores case and accents
    When I type "<text>" in the search box
    Then the card for "The City & the City" is shown

    Examples:
      | text      |
      | MIEVILLE  |
      | miéville  |
      | city & the city |

  @LIB-13
  Scenario: Search matches a phrase of the title followed by the author
    # The searched text is "<title> <author>" in lower case without accents or punctuation.
    When I type "ancillary justice ann" in the search box
    Then the result count reads "1 book match"
    When I type "ann leckie" in the search box
    Then the result count reads "5 books match"
    When I type "leckie ann" in the search box
    Then the result count reads "0 books match"

  @LIB-14 @smoke
  Scenario: No results shows a helpful empty state
    When I type "zzzzzz" in the search box
    Then the result count reads "0 books match"
    And a "No signals found" message is shown
    When I tap "Reset filters"
    Then the result count reads "1329 books match"

  # ---------- filters ----------

  @LIB-20 @smoke
  Scenario: Winners only
    When I choose "Winners only" in the "Show" filter
    Then the result count reads "296 books match"
    And every badge on the visible cards that matches the filter is a winner badge

  @LIB-21 @smoke
  Scenario Outline: Filter by one award
    When I select the "<award>" award filter
    Then the result count reads "<books> books match"
    When I choose "Winners only" in the "Show" filter
    Then the result count reads "<winners> books match"

    Examples:
      | award    | books | winners |
      | Hugo     | 361   | 74      |
      | Nebula   | 384   | 62      |
      | Clarke   | 247   | 40      |
      | Campbell | 310   | 49      |
      | Locus    | 56    | 47      |
      | PKD      | 256   | 47      |
      | BSFA     | 250   | 57      |

  @LIB-22
  Scenario: Several awards combine with "or"
    When I select the "Hugo" award filter
    And I select the "Nebula" award filter
    Then the result count reads "593 books match"
    And both pills are shown as selected
    When I select the "Hugo" award filter again
    Then the result count reads "384 books match"

  @LIB-23
  Scenario Outline: Filter by decade
    When I choose "<decade>" in the "Decade" filter
    Then the result count reads "<books> books match"
    When I choose "Winners only" in the "Show" filter
    Then the result count reads "<winners> books match"

    Examples:
      | decade | books | winners |
      | 1960s  | 71    | 15      |
      | 2010s  | 309   | 57      |
      | 2020s  | 166   | 36      |

  @LIB-24
  Scenario: Filters combine
    When I select the "Hugo" award filter
    And I choose "2010s" in the "Decade" filter
    And I choose "Winners only" in the "Show" filter
    Then only books with a Hugo win between 2010 and 2019 are shown

  @LIB-25 @smoke
  Scenario: Filter by author from a card
    When I tap the author "Arthur C. Clarke" on a card
    Then the result count reads "4 books match"
    And an "Author: Arthur C. Clarke" chip with a "Clear author" button is shown
    And the page is scrolled to the top
    When I tap "Clear author"
    Then the result count reads "1329 books match"

  @LIB-26
  Scenario: Reset filters restores every default
    Given I have typed "dune", selected "Hugo", chosen "Winners only", "1960s", "Title A–Z" and grouped by "Year"
    When I tap "Reset filters"
    Then every filter is back to its default
    And the result count reads "1329 books match"

  @LIB-27
  Scenario Outline: Filters keep their value while I use other parts of the page
    When I choose "<value>" in the "<filter>" filter
    And I open the "My Lists" tab
    And I open the "Library" tab
    Then the "<filter>" filter is still "<value>"

    Examples:
      | filter | value       |
      | Show   | Winners only |
      | Sort   | Title A–Z   |

  # ---------- grouping ----------

  @LIB-30
  Scenario: Group by year, newest first
    When I choose "Year" in the "Group by" filter
    Then the first group heading is "2026"
    And headings are in descending order
    And each heading shows how many books it holds
    And a book appears once in every year it has a nomination or win

  @LIB-31
  Scenario: Group by decade
    When I choose "Decade" in the "Group by" filter
    Then the first group heading is "2020s"
    And the last group heading is "1950s"

  @LIB-32
  Scenario: Group by award follows the standard award order
    When I choose "Award" in the "Group by" filter
    Then the group headings are, in order, "Hugo — Hugo Award", "Nebula — Nebula Award", "Clarke — Arthur C. Clarke Award", "Campbell — John W. Campbell Memorial Award", "Locus — Locus Award (SF Novel)", "PKD — Philip K. Dick Award" and "BSFA — BSFA Award"

  @LIB-33
  Scenario: Group by author sorts by surname
    When I choose "Author" in the "Group by" filter
    Then the first group heading is "Shale Aaron"

  @LIB-34
  Scenario: Within a year group winners come before finalists
    When I choose "Year" in the "Group by" filter
    And I select the "Hugo" award filter
    Then in the "2014" group the first card is "Ancillary Justice"
    And the group has 5 books

  # ---------- sorting ----------

  @LIB-40
  Scenario Outline: Sort orders
    When I choose "<sort>" in the "Sort" filter
    Then the first card is "<first>"

    Examples:
      | sort            | first                |
      | Most honoured   | Ancillary Justice    |
      | Oldest first    | The Demolished Man   |
      | Most wins       | Ancillary Justice    |

  @LIB-41
  Scenario: Newest first starts with the latest year
    When I choose "Newest first" in the "Sort" filter
    Then the first card has its latest award year equal to 2026

  @LIB-42
  Scenario: Title and author sorting
    When I choose "Title A–Z" in the "Sort" filter
    Then the card titles are in ascending locale order
    When I choose "Author A–Z" in the "Sort" filter
    Then the first card has the author "Shale Aaron"

  # ---------- helpers ----------

  @LIB-50
  Scenario: Surprise me picks an unread book that matches the filters
    Given I have selected the "Hugo" award filter
    When I tap "Surprise me"
    Then a dialog "Your next transmission" shows one book card
    And that book has a Hugo badge
    And that book is not marked read
    When I tap "Another"
    Then the dialog shows a book card again
    When I close the dialog
    Then the dialog is gone

  @LIB-51
  Scenario: Surprise me with nothing left to read
    Given I mark every book that matches the "Locus" filter as read
    When I tap "Surprise me"
    Then the toast "Nothing unread matches — widen your filters" is shown

  @LIB-52
  Scenario: Add all results to a list
    Given I have selected the "Locus" award filter
    And I have a reading list called "Locus shelf"
    When I tap "Add all results to a list"
    And I tap "Locus shelf" in the list dialog
    Then the toast "56 added to “Locus shelf”" is shown
    And the list "Locus shelf" holds 56 books

  @LIB-53
  Scenario: Add all results with no results
    Given I typed "zzzzzz" in the search box
    When I tap "Add all results to a list"
    Then the toast "No books to add" is shown

  @LIB-54 @mobile
  Scenario: The filter panel and cards fit a phone screen
    Then nothing overflows the screen horizontally
    And the header, tabs and filters are fully visible without sideways scrolling
