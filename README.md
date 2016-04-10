## Converter script for pre-release MDSynthesis Sims

Prior to the first release of MDSynthesis, a Sim could carry multiple universe
definitions. This was [removed in favor of a Sim having only a single universe](
https://github.com/datreant/MDSynthesis/issues/47), and the schema for the
state file of a Sim changed as well.

This script will convert a Sim made with the pre-release version of
MDSynthesis into one that will work with 0.6.0, making a Sim for the
specified universe name and a nested Sim for the others. All tags
and categories of the original will be preserved within each of these
Sims, and the selections for each universe will transfer as well.

Please make an issue for any problem using this script. In the future,
schema updates (if any) will be automatic, and won't require manual
intervention like this.
