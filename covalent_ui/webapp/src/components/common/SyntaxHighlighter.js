/**
 * Copyright 2021 Agnostiq Inc.
 *
 * This file is part of Covalent.
 *
 * Licensed under the GNU Affero General Public License 3.0 (the "License").
 * A copy of the License may be obtained with this software package or at
 *
 *      https://www.gnu.org/licenses/agpl-3.0.en.html
 *
 * Use of this file is prohibited except in compliance with the License. Any
 * modifications or derivative works of this file must retain this copyright
 * notice, and modified files must contain a notice indicating that they have
 * been altered from the originals.
 *
 * Covalent is distributed in the hope that it will be useful, but WITHOUT
 * ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
 * FITNESS FOR A PARTICULAR PURPOSE. See the License for more details.
 *
 * Relief from the License may be granted by purchasing a commercial license.
 */

import _ from 'lodash'
import { Light } from 'react-syntax-highlighter'
import python from 'react-syntax-highlighter/dist/esm/languages/hljs/python'
import yaml from 'react-syntax-highlighter/dist/esm/languages/hljs/yaml'
import json from 'react-syntax-highlighter/dist/esm/languages/hljs/json'
import style from 'react-syntax-highlighter/dist/cjs/styles/hljs/androidstudio'
Light.registerLanguage('python', python)
Light.registerLanguage('yaml', yaml)
Light.registerLanguage('json', json)

const SyntaxHighlighter = ({ src, ...props }) => {
  return (
    <Light
      language="python"
      style={style}
      customStyle={{
        margin: 0,
        padding: 10,
        maxHeight: 240,
        fontSize: 12,
        backgroundColor: 'transparent',
      }}
      {...props}
    >
      {_.trim(src, '"" \n')}
    </Light>
  )
}

export default SyntaxHighlighter
