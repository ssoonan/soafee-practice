// Copyright 2016 Proyectos y Sistemas de Mantenimiento SL (eProsima).
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

/*!
 * @file VideoData.hpp
 * This header file contains the declaration of the described types in the IDL file.
 *
 * This file was generated by the tool fastddsgen.
 */

#ifndef FAST_DDS_GENERATED__VIDEOMODULE_VIDEODATA_HPP
#define FAST_DDS_GENERATED__VIDEOMODULE_VIDEODATA_HPP

#include <cstdint>
#include <utility>
#include <vector>


#if defined(_WIN32)
#if defined(EPROSIMA_USER_DLL_EXPORT)
#define eProsima_user_DllExport __declspec( dllexport )
#else
#define eProsima_user_DllExport
#endif  // EPROSIMA_USER_DLL_EXPORT
#else
#define eProsima_user_DllExport
#endif  // _WIN32

#if defined(_WIN32)
#if defined(EPROSIMA_USER_DLL_EXPORT)
#if defined(VIDEODATA_SOURCE)
#define VIDEODATA_DllAPI __declspec( dllexport )
#else
#define VIDEODATA_DllAPI __declspec( dllimport )
#endif // VIDEODATA_SOURCE
#else
#define VIDEODATA_DllAPI
#endif  // EPROSIMA_USER_DLL_EXPORT
#else
#define VIDEODATA_DllAPI
#endif // _WIN32

namespace VideoModule {

/*!
 * @brief This class represents the structure VideoData defined by the user in the IDL file.
 * @ingroup VideoData
 */
class VideoData
{
public:

    /*!
     * @brief Default constructor.
     */
    eProsima_user_DllExport VideoData()
    {
    }

    /*!
     * @brief Default destructor.
     */
    eProsima_user_DllExport ~VideoData()
    {
    }

    /*!
     * @brief Copy constructor.
     * @param x Reference to the object VideoData that will be copied.
     */
    eProsima_user_DllExport VideoData(
            const VideoData& x)
    {
                    m_data = x.m_data;

    }

    /*!
     * @brief Move constructor.
     * @param x Reference to the object VideoData that will be copied.
     */
    eProsima_user_DllExport VideoData(
            VideoData&& x) noexcept
    {
        m_data = std::move(x.m_data);
    }

    /*!
     * @brief Copy assignment.
     * @param x Reference to the object VideoData that will be copied.
     */
    eProsima_user_DllExport VideoData& operator =(
            const VideoData& x)
    {

                    m_data = x.m_data;

        return *this;
    }

    /*!
     * @brief Move assignment.
     * @param x Reference to the object VideoData that will be copied.
     */
    eProsima_user_DllExport VideoData& operator =(
            VideoData&& x) noexcept
    {

        m_data = std::move(x.m_data);
        return *this;
    }

    /*!
     * @brief Comparison operator.
     * @param x VideoData object to compare.
     */
    eProsima_user_DllExport bool operator ==(
            const VideoData& x) const
    {
        return (m_data == x.m_data);
    }

    /*!
     * @brief Comparison operator.
     * @param x VideoData object to compare.
     */
    eProsima_user_DllExport bool operator !=(
            const VideoData& x) const
    {
        return !(*this == x);
    }

    /*!
     * @brief This function copies the value in member data
     * @param _data New value to be copied in member data
     */
    eProsima_user_DllExport void data(
            const std::vector<uint8_t>& _data)
    {
        m_data = _data;
    }

    /*!
     * @brief This function moves the value in member data
     * @param _data New value to be moved in member data
     */
    eProsima_user_DllExport void data(
            std::vector<uint8_t>&& _data)
    {
        m_data = std::move(_data);
    }

    /*!
     * @brief This function returns a constant reference to member data
     * @return Constant reference to member data
     */
    eProsima_user_DllExport const std::vector<uint8_t>& data() const
    {
        return m_data;
    }

    /*!
     * @brief This function returns a reference to member data
     * @return Reference to member data
     */
    eProsima_user_DllExport std::vector<uint8_t>& data()
    {
        return m_data;
    }



private:

    std::vector<uint8_t> m_data;

};

} // namespace VideoModule

#endif // _FAST_DDS_GENERATED_VIDEOMODULE_VIDEODATA_HPP_

