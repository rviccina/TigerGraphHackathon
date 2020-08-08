# Introduction
This file combines the schema script and loading job script.

## Vertex Types
- **EventMatches** are the event matches.
- **EventAwards** are the event awards.
- **EventTeams** is a list of event teams.
- **EventAlliances** are the alliances between teams.
- **EventRankings** are the rankings for each event.

## Edge Types

## <ins> Schema in Table format </ins>

**<ins>Event Matches</ins>**
| **Attribute** | **Data Type** | **Note** |
|-|-|-|
| eventKey | STRING | PK |
| matchKey | STRING |
| red1 | STRING |
| red2 | STRING |
| red3 | STRING |
| blue1 | STRING |
| blue2 | STRING |
| blue3 | STRING |
| redScore | INT |
| blueScore | INT |

**<ins>Event Awards</ins>**
| **Attribute** | **Data Type** | **Note** |
|-|-|-|
| eventKey | STRING | FK |
| awardType | STRING | Enum (will need to be converted to String) |
| awardName | STRING |  |
| team | STRING | Can be NULL |
| awardee | STRING | Can be NULL |

**<ins>Event Teams</ins>**
| **Attribute** | **Data Type** | **Note** |
|-|-|-|
| teamId | INT | PK |
| teamName | STRING |

**<ins>Event Alliances</ins>**
| **Attribute** | **Data Type** | **Note** |
|-|-|-|
| allianceId | INT | PK |
| captain | STRING |
| pick1 | STRING |
| pick2 | STRING |

**<ins>Event Rankings</ins>**
| **Attribute** | **Data Type** | **Note** |
|-|-|-|
| rankingId | INT | PK |
| rank | INT |
| team | INT |
| qs | DOUBLE |
| assist | DOUBLE |
| autoStat | DOUBLE |
| t&c | DOUBLE |
| teleop | DOUBLE |
| record | STRING |
| dq | INT |
| played | INT |

### Notes
By convention, we have put all of our CREATE VERTEX, CREATE EDGE, and the final CREATE GRAPH statements in one file.
- In default mode, a `PRIMARY_ID` is not an attribute, but the `WITH primary_id_as_attribute="true"` clause can be used to make it an attribute.  Alternately, the `PRIMARY KEY` is always an attribute; the WITH option is unneeded.
    - `PRIMARY KEY` is not supported in GraphStudio. If you decide to use this feature, you will only be able to use command line interface.

---
## Build Schema
To execute these statements, run the command file `blue_alliance_model.gsql`.  From within the shell, you would run
```
@blue_alliance_model.gsql 
```
From outside the shell, you would run 
```
> blue_alliance_model.gsql
```
---
## References
- [Defining a Graph Schema](https://docs.tigergraph.com/dev/gsql-ref/ddl-and-loading/defining-a-graph-schema)
- [setup_schema.sql](https://raw.githubusercontent.com/tigergraph/ecosys/ldbc/ldbc_benchmark/tigergraph/gsql102/3.0/setup_schema.gsql)

