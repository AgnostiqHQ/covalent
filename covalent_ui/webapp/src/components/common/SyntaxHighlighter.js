/**
 * This file is part of Covalent.
 *
 * Licensed under the Apache License 2.0 (the "License"). A copy of the
 * License may be obtained with this software package or at
 *
 *     https://www.apache.org/licenses/LICENSE-2.0
 *
 * Use of this file is prohibited except in compliance with the License.
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import _ from 'lodash'
import { Light } from 'react-syntax-highlighter'
import python from 'react-syntax-highlighter/dist/cjs/languages/hljs/python'
import yaml from 'react-syntax-highlighter/dist/cjs/languages/hljs/yaml'
import json from 'react-syntax-highlighter/dist/cjs/languages/hljs/json'
import style from 'react-syntax-highlighter/dist/cjs/styles/hljs/androidstudio'
Light.registerLanguage('python', python)
Light.registerLanguage('yaml', yaml)
Light.registerLanguage('json', json)

const SyntaxHighlighter = ({ src, ...props }) => {
  return (
    <Light
      data-testid='syntax'
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
