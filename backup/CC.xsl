<?xml version="1.0" encoding="ISO-8859-1"?>
<!-- Edited by tmackall -->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:output method="html" indent="yes" version="4.0"/>

<xsl:template match="/">
  <html>
  <body>
  <h2>Test Coverage for the Kernel</h2>
    <table width="40%" border="1">
      <tr bgcolor="#FF7F50">
        <th>Code Coverage Dates</th>
      </tr>
      <xsl:for-each select="REPORTS/entry">
      <xsl:variable name="file"><xsl:value-of select="DIR"/>/index.html</xsl:variable>
        <tr>
        <td align="center"><a href="{$file}"><xsl:value-of select="DATE"/></a></td>
        </tr>
      </xsl:for-each>
    </table>
  </body>
  </html>
</xsl:template>
</xsl:stylesheet>
