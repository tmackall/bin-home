<?xml version="1.0" encoding="ISO-8859-1"?>
<!-- Edited by XMLSpy® -->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:output method="html" indent="yes" version="4.0"/>

<xsl:template match="/">
  <html>
  <body>
  <h2>AU Test Reports by Branch</h2>
    <table width="20%" border="1">
      <tr bgcolor="#7F7F50">
        <th>Branches</th>
      </tr>
      <xsl:for-each select="REPORTS/entry">
      <xsl:variable name="file"><xsl:value-of select="BRANCH"/>.xml</xsl:variable>
        <tr>
        <td align="center"><a href="{$file}"><xsl:value-of select="BRANCH"/></a></td>
        </tr>
      </xsl:for-each>
    </table>
  </body>
  </html>
</xsl:template>
</xsl:stylesheet>
