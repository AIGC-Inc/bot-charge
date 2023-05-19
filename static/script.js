/* Cache-Control: public, max-age=3600 * 24 * 30 */
function updateContent() {
  axios.get('/permission?expire_time=expire_time')
    // .then(res => {
    //   document.querySelector('#dcontent').innerHTML = res.data
    // })
}